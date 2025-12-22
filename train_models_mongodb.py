"""
Multi-Target Air Quality Prediction Model Training (MongoDB Version)

This script trains XGBoost models using data from MongoDB instead of Excel files.
It fetches data from the ambience-3 collection and trains models for all targets.

Usage:
    python train_models_mongodb.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
import xgboost as xgb
import joblib
import warnings
import os
from pymongo import MongoClient
from dotenv import load_dotenv
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

# Set random seed for reproducibility
np.random.seed(42)

print("="*80)
print("MULTI-TARGET AIR QUALITY PREDICTION SYSTEM (MongoDB)")
print("="*80)

# ============================================================================
# STEP 1: LOAD DATA FROM MONGODB
# ============================================================================
print("\n[STEP 1] Loading data from MongoDB...")

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/milesiteaqi')
MONGO_DB = os.getenv('MONGO_DB', 'milesiteaqi')
MONGO_COLLECTION = os.getenv('MONGO_COLLECTION', 'ambience-3')

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()  # Test connection
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    
    # Count documents
    doc_count = collection.count_documents({})
    print(f"  ✓ Connected to MongoDB")
    print(f"  ✓ Collection '{MONGO_COLLECTION}' has {doc_count} documents")
    
    if doc_count == 0:
        print("\n  ✗ ERROR: No data in MongoDB collection!")
        print("  Please run 'mqtt2mongo (1).py' to collect sensor data first.")
        exit(1)
    
    # Fetch all data
    cursor = collection.find()
    data = list(cursor)
    df = pd.DataFrame(data)
    
    print(f"  ✓ Loaded {len(df)} records from MongoDB")
    
except Exception as e:
    print(f"  ✗ ERROR connecting to MongoDB: {e}")
    print("\n  Please ensure:")
    print("  1. MongoDB is running (net start MongoDB)")
    print("  2. Data collection has run (python 'mqtt2mongo (1).py')")
    exit(1)

# ============================================================================
# STEP 2: PREPROCESS DATA
# ============================================================================
print("\n[STEP 2] Preprocessing data...")

# Parse datetime and set as index
if 'received_at' in df.columns:
    df['received_at'] = pd.to_datetime(df['received_at'], errors='coerce')
    df = df.sort_values('received_at')
    df.set_index('received_at', inplace=True)
    print(f"  ✓ Set datetime index from 'received_at'")

# Drop irrelevant columns
cols_to_drop = ['_id', 'correlation_ids', 'frm_payload', 'rx_metadata', 'beep']
cols_to_drop = [col for col in cols_to_drop if col in df.columns]
if cols_to_drop:
    df.drop(columns=cols_to_drop, inplace=True)

# Keep only numeric columns
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
df = df[numeric_cols]
print(f"  ✓ Kept {len(numeric_cols)} numeric columns")
print(f"  ✓ Columns: {', '.join(numeric_cols[:5])}...")

# ============================================================================
# STEP 3: IDENTIFY TARGET VARIABLES
# ============================================================================
print("\n[STEP 3] Identifying target variables...")

# Define target pollutants to predict
target_mapping = {
    'pm2_5': 'PM2.5',
    'pm10': 'PM10',
    'co2': 'CO2',
    'tvoc': 'TVOC',
    'temperature': 'Temperature',
    'humidity': 'Humidity',
    'pressure': 'Pressure'
}

# Find actual column names for each target
target_columns = {}
for key, name in target_mapping.items():
    matching_cols = [col for col in df.columns if key in col.lower()]
    if matching_cols:
        target_columns[name] = matching_cols[0]
        print(f"  ✓ {name}: '{matching_cols[0]}'")

if not target_columns:
    print("\n  ✗ ERROR: No target columns found!")
    print(f"  Available columns: {', '.join(df.columns)}")
    exit(1)

print(f"\n  Total targets identified: {len(target_columns)}")

# ============================================================================
# STEP 4: PREPARE DATA FOR EACH TARGET
# ============================================================================
print("\n[STEP 4] Preparing data for multi-target prediction...")

# Drop columns with too many missing values (>50% missing)
missing_pct = df.isnull().sum() / len(df)
cols_to_drop = missing_pct[missing_pct > 0.5].index.tolist()
if cols_to_drop:
    df = df.drop(columns=cols_to_drop)
    print(f"  ✓ Dropped {len(cols_to_drop)} columns with >50% missing values")

# Fill missing values
print(f"  - Missing values before filling: {df.isnull().sum().sum()}")
df = df.ffill().bfill()
df = df.interpolate(method='linear', limit_direction='both')
print(f"  ✓ Missing values after filling: {df.isnull().sum().sum()}")

# Remove any remaining NaN rows
rows_before = len(df)
df = df.dropna()
print(f"  ✓ Removed {rows_before - len(df)} rows with remaining NaN values")
print(f"  ✓ Final data shape: {df.shape}")

if len(df) < 100:
    print(f"\n  ⚠ WARNING: Only {len(df)} samples available. Model quality may be poor.")
    print("  Consider collecting more data for better predictions.")

# ============================================================================
# STEP 5: TRAIN MODELS FOR EACH TARGET
# ============================================================================
print("\n[STEP 5] Training models for each target...")

# Create directory for models
os.makedirs('models', exist_ok=True)

# Store results for all models
all_results = {}
all_models = {}
all_scalers = {}

for target_name, target_col in target_columns.items():
    print(f"\n{'='*80}")
    print(f"TRAINING MODEL FOR: {target_name}")
    print(f"{'='*80}")
    
    # Prepare features (all columns except current target)
    feature_cols = [col for col in df.columns if col != target_col]
    
    # Create lag features for this target
    df_temp = df.copy()
    df_temp[f'{target_col}_lag1'] = df_temp[target_col].shift(1)
    df_temp[f'{target_col}_lag2'] = df_temp[target_col].shift(2)
    
    # Create rolling mean features for other pollutants
    rolling_window = 5
    for col in feature_cols:
        if any(keyword in col.lower() for keyword in ['pm10', 'pm2', 'co2', 'humidity', 'temperature', 'temp', 'hum', 'tvoc', 'pressure']):
            if col != target_col:
                rolling_col = f'{col}_rolling_mean_{rolling_window}'
                df_temp[rolling_col] = df_temp[col].rolling(window=rolling_window, min_periods=1).mean()
    
    # Drop NaN rows created by lag features
    df_temp = df_temp.dropna()
    
    # Prepare X and y
    all_features = [col for col in df_temp.columns if col != target_col]
    X = df_temp[all_features]
    y = df_temp[target_col]
    
    print(f"  - Feature matrix shape: {X.shape}")
    print(f"  - Target shape: {y.shape}")
    print(f"  - Target mean: {y.mean():.2f}, std: {y.std():.2f}")
    
    # Chronological split (80/20)
    split_idx = int(len(df_temp) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    print(f"  - Train set: {X_train.shape[0]} samples")
    print(f"  - Test set: {X_test.shape[0]} samples")
    
    # Normalize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train XGBoost model
    model = xgb.XGBRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        early_stopping_rounds=10,
        eval_metric='rmse',
        verbosity=0
    )
    
    eval_set = [(X_train_scaled, y_train), (X_test_scaled, y_test)]
    model.fit(X_train_scaled, y_train, eval_set=eval_set, verbose=False)
    
    print(f"  ✓ Model trained (best iteration: {model.best_iteration})")
    
    # Cross-validation
    tscv = TimeSeriesSplit(n_splits=min(5, len(X_train) // 20))
    cv_rmse_scores = []
    
    for fold, (train_idx, val_idx) in enumerate(tscv.split(X_train_scaled)):
        X_cv_train, X_cv_val = X_train_scaled[train_idx], X_train_scaled[val_idx]
        y_cv_train, y_cv_val = y_train.iloc[train_idx], y_train.iloc[val_idx]
        
        cv_model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            verbosity=0
        )
        cv_model.fit(X_cv_train, y_cv_train)
        y_cv_pred = cv_model.predict(X_cv_val)
        cv_rmse = np.sqrt(mean_squared_error(y_cv_val, y_cv_pred))
        cv_rmse_scores.append(cv_rmse)
    
    print(f"  ✓ Mean CV RMSE: {np.mean(cv_rmse_scores):.4f} +/- {np.std(cv_rmse_scores):.4f}")
    
    # Evaluate on test set
    y_train_pred = model.predict(X_train_scaled)
    y_test_pred = model.predict(X_test_scaled)
    
    train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
    test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
    train_mae = mean_absolute_error(y_train, y_train_pred)
    test_mae = mean_absolute_error(y_test, y_test_pred)
    train_r2 = r2_score(y_train, y_train_pred)
    test_r2 = r2_score(y_test, y_test_pred)
    
    print(f"\n  RESULTS:")
    print(f"    Train - RMSE: {train_rmse:.4f}, MAE: {train_mae:.4f}, R2: {train_r2:.4f}")
    print(f"    Test  - RMSE: {test_rmse:.4f}, MAE: {test_mae:.4f}, R2: {test_r2:.4f}")
    
    # Store results
    all_results[target_name] = {
        'train_rmse': train_rmse,
        'test_rmse': test_rmse,
        'train_mae': train_mae,
        'test_mae': test_mae,
        'train_r2': train_r2,
        'test_r2': test_r2,
        'cv_rmse_mean': np.mean(cv_rmse_scores),
        'cv_rmse_std': np.std(cv_rmse_scores),
        'y_test': y_test,
        'y_test_pred': y_test_pred,
        'feature_importance': pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
    }
    
    # Save model and scaler
    model_filename = f'models/{target_name.lower().replace(".", "")}_model.pkl'
    scaler_filename = f'models/{target_name.lower().replace(".", "")}_scaler.pkl'
    joblib.dump(model, model_filename)
    joblib.dump(scaler, scaler_filename)
    
    all_models[target_name] = model
    all_scalers[target_name] = scaler
    
    print(f"  ✓ Saved: {model_filename}")
    print(f"  ✓ Saved: {scaler_filename}")

# ============================================================================
# STEP 6: SUMMARY TABLE
# ============================================================================
print("\n" + "="*80)
print("MULTI-TARGET MODEL PERFORMANCE SUMMARY")
print("="*80)

summary_df = pd.DataFrame({
    'Target': list(all_results.keys()),
    'Train RMSE': [all_results[t]['train_rmse'] for t in all_results],
    'Test RMSE': [all_results[t]['test_rmse'] for t in all_results],
    'Test MAE': [all_results[t]['test_mae'] for t in all_results],
    'Test R2': [all_results[t]['test_r2'] for t in all_results],
    'CV RMSE': [all_results[t]['cv_rmse_mean'] for t in all_results]
})

print("\n" + summary_df.to_string(index=False))
print("\n" + "="*80)

# Save summary to CSV
summary_df.to_csv('models/model_performance_summary.csv', index=False)
print("\n✓ Saved performance summary to: models/model_performance_summary.csv")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*80)
print("TRAINING COMPLETE!")
print("="*80)
print(f"\n✓ Trained {len(all_results)} models for:")
for target in all_results.keys():
    print(f"  - {target}")

print(f"\n✓ Files saved:")
print(f"  - models/ directory with {len(all_results)*2} model and scaler files")
print(f"  - models/model_performance_summary.csv")
print("="*80)

print("\n✓ You can now run the prediction engine:")
print("  cd backend")
print("  python predict_and_send.py")
print("\n" + "="*80)

# Cleanup
client.close()
