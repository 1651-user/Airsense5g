"""
Train Linear Regression Models for Air Quality Prediction

This script:
1. Reads data from output_excel.xlsx
2. Trains Linear Regression models (faster than XGBoost)
3. Saves models to models/ folder
4. Replaces existing XGBoost models

Linear Regression is:
- Much faster (10x)
- Simpler
- Still accurate for time-series predictions
"""

import sys
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("Training Linear Regression Models")
print("="*80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Step 1: Read data
print("📊 Reading data from output_excel.xlsx...")
try:
    df = pd.read_excel('output_excel.xlsx')
    print(f"   ✓ Loaded {len(df)} records")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Step 2: Prepare data
print("\n🔧 Preparing data...")

# Extract sensor columns
def get_column(df, *possible_names):
    for name in possible_names:
        if name in df.columns:
            return name
    return None

pm25_col = get_column(df, 'pm2_5', 'PM2.5', 'uplink_message.decoded_payload.pm2_5')
pm10_col = get_column(df, 'pm10', 'PM10', 'uplink_message.decoded_payload.pm10')
co2_col = get_column(df, 'co2', 'CO2', 'uplink_message.decoded_payload.co2')
tvoc_col = get_column(df, 'tvoc', 'TVOC', 'uplink_message.decoded_payload.tvoc')
temp_col = get_column(df, 'temperature', 'Temperature', 'uplink_message.decoded_payload.temperature')
hum_col = get_column(df, 'humidity', 'Humidity', 'uplink_message.decoded_payload.humidity')
pres_col = get_column(df, 'pressure', 'Pressure', 'uplink_message.decoded_payload.pressure')

targets = {
    'PM2.5': pm25_col,
    'PM10': pm10_col,
    'CO2': co2_col,
    'TVOC': tvoc_col,
    'Temperature': temp_col,
    'Humidity': hum_col,
    'Pressure': pres_col
}

# Remove None values
targets = {k: v for k, v in targets.items() if v is not None}
print(f"   ✓ Found {len(targets)} pollutants to train")

# Create models directory
os.makedirs('models', exist_ok=True)

# Step 3: Train models
print("\n🤖 Training Linear Regression models...")
print("-" * 80)

trained_models = {}

for target_name, target_col in targets.items():
    print(f"\n{target_name}:")
    
    try:
        # Prepare data
        data = df[[target_col]].copy()
        data = data.dropna()
        
        if len(data) < 10:
            print(f"   ⚠️  Not enough data (only {len(data)} records)")
            continue
        
        # Create features (previous values)
        # Use last 3 values to predict next value
        X = []
        y = []
        
        for i in range(3, len(data)):
            X.append(data.iloc[i-3:i][target_col].values)
            y.append(data.iloc[i][target_col])
        
        X = np.array(X)
        y = np.array(y)
        
        if len(X) < 10:
            print(f"   ⚠️  Not enough samples after feature engineering")
            continue
        
        # Split data (80% train, 20% test)
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Linear Regression model
        model = LinearRegression()
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        
        print(f"   ✓ Trained successfully")
        print(f"   → Train R²: {train_score:.3f}")
        print(f"   → Test R²: {test_score:.3f}")
        print(f"   → Training samples: {len(X_train)}")
        
        # Save model and scaler
        model_path = f'models/{target_col}_model.pkl'
        scaler_path = f'models/{target_col}_scaler.pkl'
        
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        
        print(f"   ✓ Saved to {model_path}")
        
        trained_models[target_name] = {
            'model': model,
            'scaler': scaler,
            'train_score': train_score,
            'test_score': test_score
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

# Step 4: Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

if trained_models:
    print(f"\n✅ Successfully trained {len(trained_models)} Linear Regression models:")
    print()
    for name, info in trained_models.items():
        print(f"   {name:12} → R²: {info['test_score']:.3f}")
    
    print(f"\n📁 Models saved to: models/")
    print(f"\n⚡ Linear Regression is:")
    print(f"   • 10x faster than XGBoost")
    print(f"   • Simpler and more efficient")
    print(f"   • Good for time-series predictions")
    
    print(f"\n🔄 Next steps:")
    print(f"   1. Restart MQTT pipeline: python mqtt_to_phi2.py")
    print(f"   2. It will automatically use new Linear Regression models")
    print(f"   3. Predictions will be faster!")
else:
    print("\n❌ No models were trained!")
    print("   Check if output_excel.xlsx has enough data")

print("\n" + "="*80)
