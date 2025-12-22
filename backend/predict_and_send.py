"""
Prediction Model Integration Script

This script:
1. Loads trained XGBoost models for all air quality targets
2. Fetches latest sensor data from MongoDB
3. Generates predictions for all targets
4. Sends predictions to the backend server

Usage:
    python predict_and_send.py [--continuous]
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
from pymongo import MongoClient
from datetime import datetime
import requests
import time
import argparse
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

# Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/milesiteaqi')
MONGO_DB = os.getenv('MONGO_DB', 'milesiteaqi')
MONGO_COLLECTION = os.getenv('MONGO_COLLECTION', 'ambience-3')
MODEL_DIR = os.getenv('MODEL_DIR', '../models')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000/api/predictions')
PREDICTION_INTERVAL = int(os.getenv('PREDICTION_INTERVAL', '60'))

# Target mappings
TARGET_MODELS = {
    'PM2.5': 'pm25_model.pkl',
    'PM10': 'pm10_model.pkl',
    'CO2': 'co2_model.pkl',
    'TVOC': 'tvoc_model.pkl',
    'Temperature': 'temperature_model.pkl',
    'Humidity': 'humidity_model.pkl',
    'Pressure': 'pressure_model.pkl'
}

TARGET_SCALERS = {
    'PM2.5': 'pm25_scaler.pkl',
    'PM10': 'pm10_scaler.pkl',
    'CO2': 'co2_scaler.pkl',
    'TVOC': 'tvoc_scaler.pkl',
    'Temperature': 'temperature_scaler.pkl',
    'Humidity': 'humidity_scaler.pkl',
    'Pressure': 'pressure_scaler.pkl'
}


class PredictionEngine:
    """Air Quality Prediction Engine"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.mongo_client = None
        self.db = None
        self.collection = None
        
    def load_models(self):
        """Load all trained models and scalers"""
        print("Loading prediction models...")
        
        for target, model_file in TARGET_MODELS.items():
            model_path = os.path.join(MODEL_DIR, model_file)
            scaler_path = os.path.join(MODEL_DIR, TARGET_SCALERS[target])
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                try:
                    self.models[target] = joblib.load(model_path)
                    self.scalers[target] = joblib.load(scaler_path)
                    print(f"  ✓ Loaded {target} model")
                except Exception as e:
                    print(f"  ✗ Error loading {target} model: {e}")
            else:
                print(f"  ⚠ Model files not found for {target}")
        
        if not self.models:
            raise Exception("No models loaded! Please train models first using train_multi_target_model.py")
        
        print(f"\nSuccessfully loaded {len(self.models)} models")
        
    def connect_mongodb(self):
        """Connect to MongoDB"""
        print(f"\nConnecting to MongoDB: {MONGO_URI}")
        
        try:
            self.mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            self.mongo_client.server_info()
            self.db = self.mongo_client[MONGO_DB]
            self.collection = self.db[MONGO_COLLECTION]
            
            # Count documents
            doc_count = self.collection.count_documents({})
            print(f"  ✓ Connected to MongoDB")
            print(f"  ✓ Collection '{MONGO_COLLECTION}' has {doc_count} documents")
            
        except Exception as e:
            print(f"  ✗ MongoDB connection failed: {e}")
            raise
    
    def fetch_latest_data(self, n_samples=10):
        """Fetch latest sensor data from MongoDB"""
        try:
            # Get latest documents sorted by received_at
            cursor = self.collection.find().sort('received_at', -1).limit(n_samples)
            data = list(cursor)
            
            if not data:
                print("  ⚠ No data found in MongoDB")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Parse datetime
            if 'received_at' in df.columns:
                df['received_at'] = pd.to_datetime(df['received_at'], errors='coerce')
                df = df.sort_values('received_at')
            
            # Drop MongoDB _id and other non-numeric columns
            cols_to_drop = ['_id', 'correlation_ids', 'frm_payload', 'rx_metadata', 'beep']
            cols_to_drop = [col for col in cols_to_drop if col in df.columns]
            df = df.drop(columns=cols_to_drop)
            
            # Keep only numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            df = df[numeric_cols]
            
            print(f"  ✓ Fetched {len(df)} samples with {len(df.columns)} features")
            
            return df
            
        except Exception as e:
            print(f"  ✗ Error fetching data: {e}")
            return None
    
    def prepare_features(self, df, target_col):
        """Prepare features for prediction"""
        # Create a copy
        df_temp = df.copy()
        
        # Create lag features if target exists in data
        if target_col in df_temp.columns:
            df_temp[f'{target_col}_lag1'] = df_temp[target_col].shift(1)
            df_temp[f'{target_col}_lag2'] = df_temp[target_col].shift(2)
        
        # Create rolling mean features
        rolling_window = 5
        for col in df_temp.columns:
            if any(keyword in col.lower() for keyword in ['pm10', 'pm2', 'co2', 'humidity', 'temperature', 'temp', 'hum', 'tvoc', 'pressure']):
                if col != target_col:
                    rolling_col = f'{col}_rolling_mean_{rolling_window}'
                    df_temp[rolling_col] = df_temp[col].rolling(window=rolling_window, min_periods=1).mean()
        
        # Drop NaN rows
        df_temp = df_temp.dropna()
        
        # Remove target column from features
        feature_cols = [col for col in df_temp.columns if col != target_col]
        
        return df_temp[feature_cols]
    
    def generate_predictions(self):
        """Generate predictions for all targets"""
        print("\nFetching latest sensor data...")
        df = self.fetch_latest_data(n_samples=10)
        
        if df is None or len(df) == 0:
            print("  ✗ No data available for prediction")
            return None
        
        predictions = {
            'timestamp': datetime.now().isoformat(),
            'predictions': {}
        }
        
        print("\nGenerating predictions...")
        
        for target, model in self.models.items():
            try:
                # Find the actual column name for this target
                target_col = None
                for col in df.columns:
                    if target.lower().replace('.', '').replace(' ', '') in col.lower().replace('_', ''):
                        target_col = col
                        break
                
                if target_col is None:
                    print(f"  ⚠ Column not found for {target}, skipping")
                    continue
                
                # Prepare features
                X = self.prepare_features(df, target_col)
                
                if len(X) == 0:
                    print(f"  ⚠ No valid data for {target}")
                    continue
                
                # Get scaler
                scaler = self.scalers[target]
                
                # Scale features
                X_scaled = scaler.transform(X)
                
                # Make prediction (use last row)
                prediction = model.predict(X_scaled[-1:])
                predicted_value = float(prediction[0])
                
                # Get actual current value for comparison
                actual_value = float(df[target_col].iloc[-1])
                
                predictions['predictions'][target] = {
                    'predicted': round(predicted_value, 2),
                    'current': round(actual_value, 2),
                    'unit': self._get_unit(target)
                }
                
                print(f"  ✓ {target}: {predicted_value:.2f} {self._get_unit(target)} (current: {actual_value:.2f})")
                
            except Exception as e:
                print(f"  ✗ Error predicting {target}: {e}")
        
        # Calculate AQI from PM2.5 prediction
        if 'PM2.5' in predictions['predictions']:
            pm25_pred = predictions['predictions']['PM2.5']['predicted']
            predictions['aqi'] = self._calculate_aqi(pm25_pred)
        
        return predictions
    
    def _get_unit(self, target):
        """Get unit for target"""
        units = {
            'PM2.5': 'µg/m³',
            'PM10': 'µg/m³',
            'CO2': 'ppm',
            'TVOC': 'ppb',
            'Temperature': '°C',
            'Humidity': '%',
            'Pressure': 'hPa'
        }
        return units.get(target, '')
    
    def _calculate_aqi(self, pm25):
        """Calculate AQI from PM2.5"""
        if pm25 <= 12.0:
            return int((50 / 12.0) * pm25)
        elif pm25 <= 35.4:
            return int(50 + ((100 - 50) / (35.4 - 12.1)) * (pm25 - 12.1))
        elif pm25 <= 55.4:
            return int(100 + ((150 - 100) / (55.4 - 35.5)) * (pm25 - 35.5))
        elif pm25 <= 150.4:
            return int(150 + ((200 - 150) / (150.4 - 55.5)) * (pm25 - 55.5))
        elif pm25 <= 250.4:
            return int(200 + ((300 - 200) / (250.4 - 150.5)) * (pm25 - 150.5))
        else:
            return int(300 + ((500 - 300) / (500.4 - 250.5)) * (pm25 - 250.5))
    
    def send_to_backend(self, predictions):
        """Send predictions to backend server"""
        if not predictions or 'predictions' not in predictions:
            print("  ✗ No predictions to send")
            return False
        
        try:
            # Format data for backend
            data = {
                'timestamp': predictions['timestamp'],
                'aqi': predictions.get('aqi', 0),
                'pm25': predictions['predictions'].get('PM2.5', {}).get('predicted', 0),
                'pm10': predictions['predictions'].get('PM10', {}).get('predicted', 0),
                'co2': predictions['predictions'].get('CO2', {}).get('predicted', 0),
                'tvoc': predictions['predictions'].get('TVOC', {}).get('predicted', 0),
                'temperature': predictions['predictions'].get('Temperature', {}).get('predicted', 0),
                'humidity': predictions['predictions'].get('Humidity', {}).get('predicted', 0),
                'pressure': predictions['predictions'].get('Pressure', {}).get('predicted', 0),
                'predictions': predictions['predictions']  # Include full prediction details
            }
            
            print(f"\nSending predictions to backend: {BACKEND_URL}")
            response = requests.post(
                BACKEND_URL,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"  ✓ Successfully sent predictions (AQI: {data['aqi']})")
                return True
            else:
                print(f"  ✗ Backend returned status {response.status_code}")
                print(f"    Response: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("  ✗ Cannot connect to backend server")
            print("    Make sure server is running: python backend/server.py")
            return False
        except Exception as e:
            print(f"  ✗ Error sending predictions: {e}")
            return False
    
    def run_once(self):
        """Run prediction once"""
        predictions = self.generate_predictions()
        if predictions:
            self.send_to_backend(predictions)
        return predictions
    
    def run_continuous(self):
        """Run predictions continuously"""
        print(f"\nStarting continuous prediction mode (interval: {PREDICTION_INTERVAL}s)")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                print(f"\n{'='*80}")
                print(f"Prediction Run - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*80}")
                
                self.run_once()
                
                print(f"\nWaiting {PREDICTION_INTERVAL} seconds until next prediction...")
                time.sleep(PREDICTION_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\nStopped continuous prediction mode")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.mongo_client:
            self.mongo_client.close()
            print("\n✓ MongoDB connection closed")


def main():
    parser = argparse.ArgumentParser(description='Air Quality Prediction Engine')
    parser.add_argument('--continuous', action='store_true', 
                        help='Run predictions continuously')
    args = parser.parse_args()
    
    print("="*80)
    print("AIR QUALITY PREDICTION ENGINE")
    print("="*80)
    
    engine = PredictionEngine()
    
    try:
        # Initialize
        engine.load_models()
        engine.connect_mongodb()
        
        # Run predictions
        if args.continuous:
            engine.run_continuous()
        else:
            engine.run_once()
            
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)
    finally:
        engine.cleanup()


if __name__ == "__main__":
    main()
