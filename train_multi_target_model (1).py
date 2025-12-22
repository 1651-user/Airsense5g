

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
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

print("="*80)
print("MULTI-TARGET AIR QUALITY PREDICTION SYSTEM")
print("="*80)

# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================
print("\n[STEP 1] Loading data from Excel files...")

try:
    df1 = pd.read_excel('Sensor1+24_mar_11_20.xlsx')
    df2 = pd.read_excel('sesnor2_24_mar_11_20.xlsx')
    
    print(f"  - Sensor1 data shape: {df1.shape}")
    print(f"  - Sensor2 data shape: {df2.shape}")
    
    df = pd.concat([df1, df2], axis=0, ignore_index=True)
    print(f"  - Combined data shape: {df.shape}")
    
except Exception as e:
    print(f"ERROR loading data: {e}")
    raise

# ============================================================================
# STEP 2: PREPROCESS DATA
# ============================================================================
print("\n[STEP 2] Preprocessing data...")

# Parse datetime and set as index
if 'received_at' in df.columns:
    df['received_at'] = pd.to_datetime(df['received_at'], errors='coerce')
    df = df.sort_values('received_at')
    df.set_index('received_at', inplace=True)
    print(f"  - Set datetime index from 'received_at'")

# Drop irrelevant columns
cols_to_drop = ['correlation_ids', 'frm_payload', 'rx_metadata', 'beep']
cols_to_drop = [col for col in cols_to_drop if col in df.columns]
if cols_to_drop:
    df.drop(columns=cols_to_drop, inplace=True)

# Keep only numeric columns
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
df = df[numeric_cols]
print(f"  - Kept {len(numeric_cols)} numeric columns")

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
        print(f"  - {name}: '{matching_cols[0]}'")

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
    print(f"  - Dropped {len(cols_to_drop)} columns with >50% missing values")

# Fill missing values
print(f"  - Missing values before filling: {df.isnull().sum().sum()}")
df = df.ffill().bfill()
df = df.interpolate(method='linear', limit_direction='both')
print(f"  - Missing values after filling: {df.isnull().sum().sum()}")

# Remove any remaining NaN rows
rows_before = len(df)
df = df.dropna()
print(f"  - Removed {rows_before - len(df)} rows with remaining NaN values")
print(f"  - Final data shape: {df.shape}")

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
            if col != target_col:  # Don't create rolling mean for target itself
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
    
    print(f"  - Model trained (best iteration: {model.best_iteration})")
    
    # Cross-validation
    tscv = TimeSeriesSplit(n_splits=5)
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
    
    print(f"  - Mean CV RMSE: {np.mean(cv_rmse_scores):.4f} +/- {np.std(cv_rmse_scores):.4f}")
    
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
    
    print(f"  - Saved: {model_filename}")
    print(f"  - Saved: {scaler_filename}")

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
print("\nSaved performance summary to: models/model_performance_summary.csv")

# ============================================================================
# STEP 7: VISUALIZATIONS
# ============================================================================
print("\n[STEP 7] Creating comprehensive visualizations...")

# Create a large figure with subplots for each target
n_targets = len(all_results)
fig, axes = plt.subplots(n_targets, 3, figsize=(18, 5*n_targets))

if n_targets == 1:
    axes = axes.reshape(1, -1)

for idx, (target_name, results) in enumerate(all_results.items()):
    y_test = results['y_test']
    y_test_pred = results['y_test_pred']
    
    # Plot 1: Actual vs Predicted
    axes[idx, 0].scatter(y_test, y_test_pred, alpha=0.5, s=10)
    axes[idx, 0].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    axes[idx, 0].set_xlabel(f'Actual {target_name}', fontsize=10)
    axes[idx, 0].set_ylabel(f'Predicted {target_name}', fontsize=10)
    axes[idx, 0].set_title(f'{target_name}: Actual vs Predicted\nRMSE: {results["test_rmse"]:.4f}, R2: {results["test_r2"]:.4f}', 
                           fontsize=11, fontweight='bold')
    axes[idx, 0].grid(True, alpha=0.3)
    
    # Plot 2: Time Series (last 200 samples)
    n_samples = min(200, len(y_test))
    axes[idx, 1].plot(y_test.iloc[-n_samples:].values, label='Actual', linewidth=1.5, alpha=0.7)
    axes[idx, 1].plot(y_test_pred[-n_samples:], label='Predicted', linewidth=1.5, alpha=0.7)
    axes[idx, 1].set_xlabel('Time Index', fontsize=10)
    axes[idx, 1].set_ylabel(target_name, fontsize=10)
    axes[idx, 1].set_title(f'{target_name}: Time Series Prediction', fontsize=11, fontweight='bold')
    axes[idx, 1].legend(fontsize=9)
    axes[idx, 1].grid(True, alpha=0.3)
    
    # Plot 3: Feature Importance (Top 10)
    top_features = results['feature_importance'].head(10)
    axes[idx, 2].barh(range(len(top_features)), top_features['importance'].values)
    axes[idx, 2].set_yticks(range(len(top_features)))
    axes[idx, 2].set_yticklabels([f[:30] for f in top_features['feature'].values], fontsize=8)
    axes[idx, 2].set_xlabel('Importance', fontsize=10)
    axes[idx, 2].set_title(f'{target_name}: Top 10 Features', fontsize=11, fontweight='bold')
    axes[idx, 2].invert_yaxis()
    axes[idx, 2].grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('multi_target_evaluation.png', dpi=300, bbox_inches='tight')
print("  - Saved: multi_target_evaluation.png")

# Create comparison bar chart
fig2, ax = plt.subplots(1, 1, figsize=(12, 6))
x = np.arange(len(summary_df))
width = 0.25

ax.bar(x - width, summary_df['Train RMSE'], width, label='Train RMSE', alpha=0.8)
ax.bar(x, summary_df['Test RMSE'], width, label='Test RMSE', alpha=0.8)
ax.bar(x + width, summary_df['CV RMSE'], width, label='CV RMSE', alpha=0.8)

ax.set_xlabel('Target Variable', fontsize=12, fontweight='bold')
ax.set_ylabel('RMSE', fontsize=12, fontweight='bold')
ax.set_title('Model Performance Comparison Across All Targets', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(summary_df['Target'], rotation=45, ha='right')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('model_comparison.png', dpi=300, bbox_inches='tight')
print("  - Saved: model_comparison.png")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*80)
print("TRAINING COMPLETE!")
print("="*80)
print(f"\nTrained {len(all_results)} models for:")
for target in all_results.keys():
    print(f"  - {target}")

print(f"\nFiles saved:")
print(f"  - models/ directory with {len(all_results)*2} model and scaler files")
print(f"  - models/model_performance_summary.csv")
print(f"  - multi_target_evaluation.png")
print(f"  - model_comparison.png")
print("="*80)
