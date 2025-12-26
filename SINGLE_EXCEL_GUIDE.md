# ✅ Single Excel File System - Setup Complete!

## 🎯 **What You Wanted**

You wanted:
1. ✅ **One single Excel file** (`output_excel.xlsx`)
2. ✅ **Append new data** to this file (don't create new files)
3. ✅ **Update automatically** when you run the script

## ✅ **What I Did**

### **Created: `update_excel.py`**

This script:
1. 📄 Reads new data from `mqtt_data.json`
2. 📁 Opens existing `output_excel.xlsx`
3. 🔄 Appends new records
4. 🧹 Removes duplicates (based on timestamp)
5. 📅 Sorts data chronologically
6. 💾 Saves back to `output_excel.xlsx`

**No new files created!** ✅

---

## 📊 **Current Status**

### **Your Excel File: `output_excel.xlsx`**

- ✅ **Total records:** 802
- ✅ **Date range:** Dec 3 - Dec 26, 2025 (22 days)
- ✅ **Columns:** 57 sensor fields
- ✅ **Duplicates removed:** 112
- ✅ **Sorted:** By timestamp (oldest to newest)

---

## 🚀 **How to Use**

### **Workflow:**

```
MQTT Sensor → mqtt_data.json → update_excel.py → output_excel.xlsx → AI
```

### **Commands:**

#### **1. Update Excel with New Data**
```powershell
python update_excel.py
```

This will:
- Read new data from `mqtt_data.json`
- Append to `output_excel.xlsx`
- Remove duplicates
- Sort by timestamp

#### **2. Send Excel Data to AI**
```powershell
python send_excel_to_ai.py
```

This will:
- Read latest data from `output_excel.xlsx`
- Generate predictions
- Send to backend for AI chat

---

## 🔄 **Complete Workflow**

### **When You Want to Update Everything:**

```powershell
# Step 1: Update Excel with new MQTT data
python update_excel.py

# Step 2: Send latest Excel data to AI
python send_excel_to_ai.py
```

**That's it!** Your AI will now have the latest data.

---

## 📱 **Then Test in Flutter App**

1. Open your Flutter app
2. Go to Chat screen
3. Ask:
   - **"Show the pollutant levels"** → Shows current values
   - **"What are the predictions?"** → Shows predicted values
   - **"Is the air quality safe?"** → Health recommendations

---

## 🎯 **Key Features**

### ✅ **No More Multiple Excel Files**
- Before: `mqtt_data_20251226_112200.xlsx`, `mqtt_data_20251226_112622.xlsx`, etc.
- After: Just one file → `output_excel.xlsx`

### ✅ **Automatic Deduplication**
- Removes duplicate records based on timestamp
- Keeps only unique sensor readings

### ✅ **Chronological Sorting**
- Data is always sorted from oldest to newest
- Easy to track trends over time

### ✅ **Cumulative Data**
- New data is appended, not replaced
- Historical data is preserved
- Currently: 22 days of data (Dec 3-26)

---

## 📊 **Data Summary**

### **What's in `output_excel.xlsx`:**

| Metric | Value |
|--------|-------|
| **Total Records** | 802 |
| **Date Range** | Dec 3 - Dec 26, 2025 |
| **Days Covered** | 22 days |
| **Columns** | 57 sensor fields |
| **Latest Update** | Dec 26, 2025 07:13 AM |

### **Sensor Fields Include:**
- PM2.5, PM10
- CO2, TVOC
- Temperature, Humidity, Pressure
- Battery, Light Level, PIR
- Timestamps
- And more...

---

## 🔧 **Modified Scripts**

### **1. `update_excel.py` (NEW)**
- Appends new data to `output_excel.xlsx`
- Removes duplicates
- Sorts by timestamp

### **2. `send_excel_to_ai.py` (UPDATED)**
- Now reads from `output_excel.xlsx` (not mqtt_data_*.xlsx)
- Sends latest data to AI backend

---

## 📝 **Quick Reference**

| Task | Command |
|------|---------|
| **Update Excel** | `python update_excel.py` |
| **Send to AI** | `python send_excel_to_ai.py` |
| **Both at once** | `python update_excel.py && python send_excel_to_ai.py` |
| **Check status** | `python check_system_status.py` |

---

## 🎯 **Example Usage**

### **Scenario: New MQTT Data Arrived**

```powershell
# 1. Update Excel with new data
python update_excel.py

# Output:
# ✓ Loaded 57 records from JSON
# ✓ Found existing file with 802 rows
# ✓ Combined: 859 total rows
# ✓ Removed 0 duplicates
# ✓ Unique records: 859
# ✓ Excel file updated successfully!

# 2. Send to AI
python send_excel_to_ai.py

# Output:
# ✓ Found: output_excel.xlsx
# ✓ Loaded 859 records
# ✓ Latest record: Dec 26, 2025
# ✓ SUCCESS! Data sent to backend
```

### **Then in Flutter App:**

Ask: **"Show the pollutant levels"**

AI Response:
```
Based on current sensor readings:

Air Quality Index: 162 (Unhealthy)

CURRENT SENSOR READINGS:
  • PM2.5: 79.0 µg/m³
  • PM10: 96.0 µg/m³
  • CO2: 400.0 ppm
  ...
```

---

## 🔄 **Automatic Updates (Optional)**

### **Option 1: Manual (Current)**
Run commands when you want to update:
```powershell
python update_excel.py
python send_excel_to_ai.py
```

### **Option 2: Scheduled Task**
Set up Windows Task Scheduler to run every hour:
1. Open Task Scheduler
2. Create task: "Update AirSense Excel"
3. Trigger: Every 1 hour
4. Action: Run `update_excel.py` then `send_excel_to_ai.py`

### **Option 3: Auto-Sync Script**
Use `auto_sync_mqtt.py` to automatically update when new data arrives.

---

## ✅ **Benefits**

### **Before (Multiple Files):**
- ❌ New file created each time
- ❌ Data scattered across files
- ❌ Need to combine manually
- ❌ Duplicates everywhere

### **After (Single File):**
- ✅ One file: `output_excel.xlsx`
- ✅ All data in one place
- ✅ Automatic deduplication
- ✅ Chronologically sorted
- ✅ Easy to manage

---

## 📊 **File Structure**

```
Airsense5g/
├── mqtt_data.json          ← Latest MQTT data (100 records)
├── output_excel.xlsx       ← YOUR MAIN FILE (802 records, 22 days)
├── update_excel.py         ← Run this to update Excel
├── send_excel_to_ai.py     ← Run this to send to AI
└── ...
```

---

## 🎉 **Summary**

**You now have:**
- ✅ One single Excel file: `output_excel.xlsx`
- ✅ 802 records spanning 22 days
- ✅ Automatic append (no new files)
- ✅ Automatic deduplication
- ✅ Chronological sorting
- ✅ AI integration ready

**To update:**
```powershell
python update_excel.py
python send_excel_to_ai.py
```

**That's it!** Your system is now streamlined and easy to maintain! 🚀

---

**Status:** 🟢 **READY TO USE!**

File: `output_excel.xlsx` | Records: **802** | Range: **22 days**
