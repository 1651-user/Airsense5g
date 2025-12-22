"""
Quick Training Script using output.xlsx

This script trains models using the existing output.xlsx file.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import xgboost as xgb
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

print("="*80)
print("TRAINING AIR QUALITY PREDICTION MODELS")
print("="*80)

# Load data
print("\n[1/4] Loading data from output.xlsx...")
df = pd.read_excel('output.xlsx')
print(f"  OK Loaded {len(df)} records")

# Extract sensor data columns
sensor_cols = [col for col in df.columns if 'uplink_message.decoded_payload' in col]
df_sensor = df[sensor_cols].copy()

# Rename columns (remove prefix)
df_sensor.columns = [col.replace('uplink_message.decoded_payload.', '') for col in df_sensor.columns]
print(f"  OK Found {len(df_sensor.columns)} sensor columns")

# Add timestamp
if 'received_at' in df.columns:
    df_sensor['received_at'] = pd.to_datetime(df['received_at'])
    df_sensor = df_sensor.sort_values('received_at')
    df_sensor.set_index('received_at', inplace=True)

# Drop non-numeric and irrelevant columns
df_sensor = df_sensor.select_dtypes(include=[np.number])
df_sensor = df_sensor.dropna(how='all', axis=1)  # Drop columns that are all NaN
df_sensor = df_sensor.fillna(method='ffill').fillna(method='bfill')
df_sensor = df_sensor.dropna()

print(f"  OK Cleaned data: {df_sensor.shape}")
print(f"  OK Columns: {', '.join(df_sensor.columns)}")

# Define targets
target_mapping = {
    'pm2_5': 'PM2.5',
    'pm10': 'PM10',
    'co2': 'CO2',
    'tvoc': 'TVOC',
    'temperature': 'Temperature',
    'humidity': 'Humidity',
    'pressure': 'Pressure'
}

targets = {}
for key, name in target_mapping.items():
    cols = [c for c in df_sensor.columns if key in c.lower()]
    if cols:
        targets[name] = cols[0]
        print(f"  OK Target {name}: {cols[0]}")

if not targets:
    print("\n  ERROR No target columns found!")
    exit(1)

# Create models directory
os.makedirs('models', exist_ok=True)

print(f"\n[2/4] Training {len(targets)} models...")

results = {}
for target_name, target_col in targets.items():
    print(f"\n  Training {target_name}...")
    
    # Prepare data
    X = df_sensor.drop(columns=[target_col])
    y = df_sensor[target_col]
    
    # Split
    split_idx = int(len(df_sensor) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    # Scale
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train
    model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
        verbosity=0
    )
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print(f"    RMSE: {rmse:.4f}, R²: {r2:.4f}")
    
    # Save
    model_file = f'models/{target_name.lower().replace(".", "")}_model.pkl'
    scaler_file = f'models/{target_name.lower().replace(".", "")}_scaler.pkl'
    joblib.dump(model, model_file)
    joblib.dump(scaler, scaler_file)
    
    results[target_name] = {'rmse': rmse, 'r2': r2}

print(f"\n[3/4] Saving summary...")
summary = pd.DataFrame(results).T
summary.to_csv('models/model_performance_summary.csv')
print(f"  OK Saved to models/model_performance_summary.csv")

print(f"\n[4/4] Summary:")
print(summary)

print("\n" + "="*80)
print("OK TRAINING COMPLETE!")
print(f"OK Trained {len(targets)} models")
print(f"OK Saved {len(targets)*2} files to models/")
print("="*80)
print("\nOK Next: Run predictions with:")
print("  cd backend")
print("  python predict_and_send.py")
print("="*80)
