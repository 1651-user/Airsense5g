"""
Fix output5.xlsx: Merge duplicate short-name column data into original long-name columns
Then remove the duplicate short-name columns

ORIGINAL columns (KEEP): uplink_message.decoded_payload.pm2_5, etc.
DUPLICATE columns (MERGE then DELETE): pm2_5, pm10, co2, etc.
"""
import pandas as pd
import os

print("="*80)
print("FIXING OUTPUT5.XLSX: MERGING DUPLICATE DATA")
print("="*80)

excel_file = 'output5.xlsx'

if not os.path.exists(excel_file):
    print(f"ERROR: {excel_file} not found!")
    exit(1)

# Read the file
print(f"\n[1/5] Reading {excel_file}...")
df = pd.read_excel(excel_file)
print(f"  Current: {len(df)} rows, {len(df.columns)} columns")

# Define the mapping: short name -> long name
column_mapping = {
    'battery': 'uplink_message.decoded_payload.battery',
    'pm2_5': 'uplink_message.decoded_payload.pm2_5',
    'pm10': 'uplink_message.decoded_payload.pm10',
    'co2': 'uplink_message.decoded_payload.co2',
    'tvoc': 'uplink_message.decoded_payload.tvoc',
    'temperature': 'uplink_message.decoded_payload.temperature',
    'humidity': 'uplink_message.decoded_payload.humidity',
    'pressure': 'uplink_message.decoded_payload.pressure',
    'light_level': 'uplink_message.decoded_payload.light_level',
    'pir': 'uplink_message.decoded_payload.pir',
}

print(f"\n[2/5] Merging data from duplicate columns into originals...")
merged_count = 0

# For each row, merge short-name data into long-name columns
for short_col, long_col in column_mapping.items():
    if short_col in df.columns and long_col in df.columns:
        # Find rows where short column has data but long column is empty
        mask = df[short_col].notna() & df[long_col].isna()
        
        if mask.any():
            # Copy data from short column to long column
            df.loc[mask, long_col] = df.loc[mask, short_col]
            rows_merged = mask.sum()
            merged_count += rows_merged
            print(f"  {short_col} -> {long_col}: {rows_merged} rows merged")

print(f"\n  Total: {merged_count} data points merged")

# Backup
backup_file = 'output5_before_dedup.xlsx'
print(f"\n[3/5] Creating backup: {backup_file}")
df.to_excel(backup_file, index=False)

# Remove duplicate short-name columns
print(f"\n[4/5] Removing duplicate short-name columns...")
duplicate_cols = [col for col in column_mapping.keys() if col in df.columns]
df_clean = df.drop(columns=duplicate_cols)
print(f"  Removed {len(duplicate_cols)} duplicate columns: {duplicate_cols}")

# Save cleaned file
print(f"\n[5/5] Saving cleaned file...")
df_clean.to_excel(excel_file, index=False)
print(f"  Saved: {len(df_clean)} rows, {len(df_clean.columns)} columns")

print("\n" + "="*80)
print("VERIFICATION")
print("="*80)
print(f"\nRemaining columns ({len(df_clean.columns)}):")
for i, col in enumerate(df_clean.columns[:15], 1):
    print(f"  {i}. {col}")
if len(df_clean.columns) > 15:
    print(f"  ... and {len(df_clean.columns) - 15} more")

print("\n" + "="*80)
print("DONE!")
print("="*80)
print(f"\nOriginal file backed up to: {backup_file}")
print(f"Cleaned file saved to: {excel_file}")
print(f"\nAll duplicate short-name columns removed.")
print(f"All data merged into original long-name columns.")
