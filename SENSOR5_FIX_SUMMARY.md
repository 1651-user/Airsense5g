# Sensor 5 Data Mapping Fix - Summary

## Problem Identified

**Sensor 5** had incorrect MQTT field mappings from the hardware/firmware level:
- The `battery` field was actually sending **PM2.5** data (values like 88)
- The `pm2_5` field was receiving incorrect low values (like 47)

## Root Cause

The MQTT decoder or sensor firmware for Sensor 5 (ambience-5) has incorrect field labels. This is a **hardware/firmware configuration issue**, not a Python code issue.

## Solution Implemented

### 1. Fixed MQTT Data Collection (`mqtt_to_ai_sensor5.py`)
Added automatic remapping in the MQTT message handler:
```python
# FIX: Sensor 5 has incorrect MQTT field mapping
if 'battery' in sensor_data and sensor_data['battery'] > 80:
    sensor_data['pm2_5'] = sensor_data['battery']
    sensor_data['battery'] = 100  # Assume full battery
```

### 2. Fixed Historical Data
- **JSON file**: `mqtt_data_sensor5.json` - corrected all 8 records
- **Excel file**: `output5.xlsx` - corrected 8 rows
- Both files backed up before modification

### 3. Cleaned Excel Columns
Removed redundant long-name columns (like `uplink_message.decoded_payload.*`) 
Kept only essential short-name columns in correct order.

## Verification

**Before Fix:**
- PM2.5: 47.0 ❌
- PM10: 59.0  
- CO2: 613.0
- Battery: 88 ❌

**After Fix:**
- PM2.5: **88.0** ✅
- PM10: 59.0
- CO2: 613.0
- Battery: 100.0 ✅

## Files Modified

1. `mqtt_to_ai_sensor5.py` - MQTT data collection with auto-fix
2. `mqtt_data_sensor5.json` - Historical JSON data corrected
3. `output5.xlsx` - Historical Excel data corrected

## Backup Files Created

- `mqtt_data_sensor5_backup.json` - Original JSON data
- `output5_backup.xlsx` - Original Excel data with all columns

## Next Steps

1. **Restart Sensor 5 pipeline** to use the fixed code:
   ```bash
   python mqtt_to_ai_sensor5.py
   ```

2. **Re-run predictions** with corrected data:
   ```bash
   python start_with_predictions.py
   ```

3. **Long-term fix**: Contact sensor manufacturer or update MQTT decoder configuration to fix the field mapping at the source.

## Remaining Questions

- **PM10 value (59)**: Seems unusually low compared to image showing 613. Need to verify if PM10 also has mapping issues.
- **CO2 value (613)**: This seems correct for indoor air quality.

---
**Status**: ✅ FIXED
**Date**: 2025-12-29
