import pandas as pd
import numpy as np

# Quick test to see why PM2.5 predictions are missing
df = pd.read_excel('output3.xlsx')
df_recent = df.tail(100)

# Find PM2.5 columns
target_columns = ['pm2_5', 'pm10', 'co2', 'tvoc', 'temperature', 'humidity', 'pressure']
all_columns = df_recent.columns.tolist()

print("Finding PM2.5 column...")
for target in target_columns:
    short_col = target if target in all_columns else None
    long_col = None
    
    for col in all_columns:
        if target in col.lower() and 'decoded_payload' in col.lower():
            long_col = col
            break
    
    if target == 'pm2_5':
        print(f"\nPM2.5 Detection:")
        print(f"  Short column '{target}' exists: {short_col is not None}")
        print(f"  Long column exists: {long_col is not None}")
        
        if short_col and long_col:
            short_data = df_recent[short_col].notna().sum()
            long_data = df_recent[long_col].notna().sum()
            print(f"  Short column data count: {short_data}/100")
            print(f"  Long column data count: {long_data}/100")
            chosen = long_col if long_data > short_data else short_col
            print(f"  Chosen column: {chosen}")
            
            # Check clean data after extraction
            df_extracted = pd.DataFrame()
            df_extracted['pm2_5'] = df_recent[chosen]
            df_clean = df_extracted[['pm2_5']].dropna()
            print(f"  Clean values after dropna: {len(df_clean)}")
            print(f"  Last 5 values: {df_clean['pm2_5'].tail(5).tolist()}")
            
            if len(df_clean) >= 3:
                print(f"  ✓ ENOUGH DATA FOR PREDICTION")
            else:
                print(f"  ✗ NOT ENOUGH DATA (need 3+)")
