# 📊 Why Past Two Days' Data Is Not in Excel Sheet

## 🔍 **Problem Identified**

Your `mqtt_data.json` file **only keeps the last 100 records**, not all historical data. This is by design in the MQTT pipeline.

### **Current Situation:**
- ✅ You have **52 records** in `mqtt_data.json`
- ✅ Data spans **4 days** (Dec 22 - Dec 26)
- ⚠️ Only **2 records** are from the past 2 days
- ⚠️ Most data is **older** (from Dec 22-24)

### **Why This Happens:**
The MQTT pipeline (`mqtt_to_phi2.py` line 209) automatically **limits** the JSON file to 100 records:

```python
# Keep only last 100 entries
if len(existing_data) > 100:
    existing_data = existing_data[-100:]
```

This means:
- Older records are **automatically deleted**
- Only the **most recent 100 messages** are kept
- Data is **not accumulated** over days

---

## ✅ **Solutions**

### **Solution 1: Use Existing Excel Exports** (Recommended)

You already have Excel files with historical data:

| File | Date | Records |
|------|------|---------|
| `mqtt_data_20251226_112622.xlsx` | Dec 26 (Today) | ~52 |
| `mqtt_data_20251223_160444.xlsx` | Dec 23 | ~50 |
| `mqtt_data_20251222_131326.xlsx` | Dec 22 | ~35 |

**To get past 2 days' data:**
1. Combine these Excel files
2. Use the script below to merge them

### **Solution 2: Combine Multiple Excel Files**

I'll create a script to merge all your Excel exports:

```bash
python combine_excel_files.py
```

This will create a single Excel file with all historical data.

### **Solution 3: Increase JSON Storage Limit**

Modify `mqtt_to_phi2.py` to keep more records:

**Line 209:** Change from `100` to `1000` or higher:
```python
# Keep only last 1000 entries (instead of 100)
if len(existing_data) > 1000:
    existing_data = existing_data[-1000:]
```

**Pros:** More historical data in JSON
**Cons:** Larger file size, slower processing

### **Solution 4: Use Database for Long-term Storage** (Best for Production)

For permanent historical storage, use MongoDB:
- All data is stored permanently
- No automatic deletion
- Better for analytics
- See `train_models_mongodb.py` for example

---

## 🔧 **Quick Fix: Combine Excel Files**

I'll create a script to merge all your Excel exports into one file with complete historical data.
