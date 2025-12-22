#!/bin/bash
# MQTT to TinyLlama Pipeline (Linux version)

echo "================================================================================"
echo "MQTT TO TINYLLAMA PIPELINE"
echo "================================================================================"
echo ""
echo "This pipeline will:"
echo "  1. Connect to MQTT broker (am3 sensor)"
echo "  2. Save data to JSON file (mqtt_data.json)"
echo "  3. Generate predictions using trained models"
echo "  4. Send predictions to backend server"
echo "  5. TinyLlama receives predictions as context"
echo ""
echo "================================================================================"
echo ""

# Check if models exist
if [ ! -f "models/pm25_model.pkl" ]; then
    echo "ERROR: Models not found!"
    echo "Please train models first: python3 train_quick.py"
    echo ""
    exit 1
fi

echo "[OK] Models found"
echo ""

# Check if backend is running
echo "[INFO] Make sure backend server is running in another terminal:"
echo "       cd backend"
echo "       python3 server.py"
echo ""
echo "[INFO] Make sure LM Studio is running with TinyLlama"
echo ""

read -p "Press Enter to continue..."

echo ""
echo "Starting pipeline..."
echo "Press Ctrl+C to stop"
echo ""

python3 mqtt_to_tinyllama.py
