# Excel Column Mapping Fix - Summary

## Problem

When new MQTT data arrived, the Excel sync scripts were **creating NEW columns** instead of putting data into **EXISTING columns**.

This caused:
- Duplicate column headings
- Messy Excel files with 40-50+ columns
- Data spread across different columns instead of organized

## Root Cause

In `simple_excel_sync.py` and `excel_integration.py`:
```python
# OLD CODE (WRONG):
df_combined = pd.concat([df_existing, df_new], ignore_index=True)
```

When pandas concatenates DataFrames with different column names, it **creates new columns** for any fields that don't exist in the original DataFrame.

## Solution

**Modified both sync scripts to:**

1. **Check existing Excel columns** before adding new data
2. **Filter new data** to ONLY include columns that already exist
3. **Add missing columns as None** if data is missing
4. **Reorder columns** to match existing Excel structure

```python
# NEW CODE (CORRECT):
if existing_columns:
    # Keep only columns that exist in the Excel file
    df_new = df_new[[col for col in df_new.columns if col in existing_columns]]
    
    # Add missing columns with NaN values
    for col in existing_columns:
        if col not in df_new.columns:
            df_new[col] = None
    
    # Reorder columns to match existing Excel
    df_new = df_new[existing_columns]

df_combined = pd.concat([df_existing, df_new], ignore_index=True)
```

##Files Modified

1. ✅ **`simple_excel_sync.py`**
   - Updated `sync_json_to_excel()` function
   - Now maps new data to existing columns ONLY

2. ✅ **`excel_integration.py`**
   - Updated `append_to_excel()` function
   - Now maps new data to existing columns ONLY

## Expected Behavior (After Fix)

### Before:
- Excel file: 12 columns
- <New MQTT data arrives with field "uplink_message.decoded_payload.pm2_5">
- Result: 13 columns (new column created) ❌

### After:
- Excel file: 12 columns (`pm2_5`, `pm10`, `co2`, etc.)
- New MQTT data arrives with field "pm2_5"
- Result: 12 columns (data goes to existing `pm2_5` column) ✅

## Testing

To test the fix:
1. Close `output5.xlsx` in Excel
2. Run: `python simple_excel_sync.py`
3. New MQTT data will be saved to EXISTING columns
4. No new columns will be created

## Current Excel Column Structure (All Sensors)

All sensor Excel files now have these 12 columns:
1. `received_at`
2. `sensor_id`
3. `battery`
4. `pm2_5`
5. `pm10`
6. `co2`
7. `tvoc`
8. `temperature`
9. `humidity`
10. `pressure`
11. `light_level`
12. `pir`

**New data will ALWAYS be saved to these exact columns. No new columns will be created.**

---

**Status**: ✅ FIXED
**Date**: 2025-12-29
**Issue**: New data creating duplicate columns
**Solution**: Map new data to existing column names only
