# Quick Start Guide - AirSense5g

## 🚀 One-Click Startup

### Step 1: Start All Services

**Double-click this file:**
```
START_ALL.bat
```

This will automatically start:
- ✅ Backend Server (http://localhost:5000)
- ✅ MQTT Pipeline (Data collection)

**Two new windows will open - KEEP THEM OPEN!**

### Step 2: Start Flutter App

Open a new terminal and run:
```bash
flutter run
```

### Step 3: Use Your App!

- 📊 **Dashboard** - Shows live sensor data
- 💬 **Chat** - Ask Phi-2 about air quality
- 🗺️ **Map** - View sensor locations

---

## 📍 Important URLs

| Service | URL | Status Check |
|---------|-----|--------------|
| **Backend API** | http://localhost:5000 | http://localhost:5000/health |
| **Latest Predictions** | http://localhost:5000/api/predictions/latest | - |
| **LM Studio (Phi-2)** | http://192.168.1.16:1234 | Auto-connected |

---

## 🛑 How to Stop

1. Close the **Backend Server** window
2. Close the **MQTT Pipeline** window
3. Stop your Flutter app (Ctrl+C or stop in IDE)

---

## ✅ System Requirements

Before running `START_ALL.bat`, make sure:

1. ✅ **LM Studio is running** with Phi-2 loaded
2. ✅ **Python packages installed:**
   ```bash
   pip install flask flask-cors requests python-dotenv paho-mqtt pandas numpy xgboost scikit-learn joblib
   ```
3. ✅ **Models trained** (run `python train_quick.py` if needed)

---

## 🔧 Troubleshooting

### Backend won't start
- Check if port 5000 is already in use
- Make sure you're in the project directory

### MQTT not connecting
- Check internet connection
- Verify MQTT credentials in `am3.env`

### Phi-2 not responding with data
- Make sure backend is running
- Check if prediction data exists: http://localhost:5000/api/predictions/latest
- Restart the backend if needed

---

## 📝 Daily Workflow

1. **Morning:**
   - Run `START_ALL.bat`
   - Wait for both windows to open
   - Run `flutter run`

2. **During the day:**
   - Keep backend and MQTT windows open
   - App will auto-refresh data every 30 seconds

3. **Evening:**
   - Close backend and MQTT windows
   - Stop Flutter app

**That's it! Your complete air quality monitoring system with AI chat!** 🎉
