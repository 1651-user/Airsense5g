"""
Example script to send prediction data to the AirSense backend server.

This script demonstrates how to integrate your prediction model with the backend.
Modify this to match your actual prediction model's output format.

Usage:
    python send_prediction.py
"""

import requests
import json
from datetime import datetime
import time

# Backend server URL
BACKEND_URL = "http://localhost:5000/api/predictions"

def send_prediction_data(aqi, pm25, pm10, co2, no2, location=None, forecast=None):
    """
    Send prediction data to the backend server
    
    Args:
        aqi (int): Air Quality Index value
        pm25 (float): PM2.5 concentration in µg/m³
        pm10 (float): PM10 concentration in µg/m³
        co2 (float): CO2 concentration in ppm
        no2 (float): NO2 concentration in ppb
        location (dict, optional): Location data with 'lat', 'lon', 'name'
        forecast (list, optional): List of forecast data points
    
    Returns:
        dict: Response from the server
    """
    
    # Prepare the data payload
    data = {
        "timestamp": datetime.now().isoformat(),
        "aqi": aqi,
        "pm25": pm25,
        "pm10": pm10,
        "co2": co2,
        "no2": no2,
    }
    
    if location:
        data["location"] = location
    
    if forecast:
        data["forecast"] = forecast
    
    try:
        # Send POST request to backend
        response = requests.post(
            BACKEND_URL,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✓ Successfully sent prediction data (AQI: {aqi})")
            return response.json()
        else:
            print(f"✗ Error: Server returned status {response.status_code}")
            print(f"  Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("✗ Error: Cannot connect to backend server")
        print("  Make sure the server is running: python backend/server.py")
        return None
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None


def example_usage():
    """
    Example usage with sample data
    """
    
    print("AirSense Prediction Data Sender")
    print("=" * 50)
    print()
    
    # Example 1: Send basic prediction data
    print("Sending sample prediction data...")
    result = send_prediction_data(
        aqi=85,
        pm25=35.5,
        pm10=50.2,
        co2=400,
        no2=20,
        location={
            "lat": 12.9716,
            "lon": 77.5946,
            "name": "Bangalore, India"
        }
    )
    
    if result:
        print(f"  Server response: {result}")
    
    print()
    
    # Example 2: Send prediction with forecast
    print("Sending prediction with forecast...")
    forecast_data = [
        {
            "timestamp": datetime.now().isoformat(),
            "aqi": 90,
            "pm25": 38.0
        },
        {
            "timestamp": datetime.now().isoformat(),
            "aqi": 95,
            "pm25": 40.5
        }
    ]
    
    result = send_prediction_data(
        aqi=85,
        pm25=35.5,
        pm10=50.2,
        co2=400,
        no2=20,
        forecast=forecast_data
    )
    
    if result:
        print(f"  Server response: {result}")


def continuous_monitoring():
    """
    Example of continuous monitoring - sends data every 60 seconds
    
    Replace this with your actual prediction model's output
    """
    
    print("Starting continuous monitoring mode...")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        while True:
            # TODO: Replace this with your actual prediction model
            # Example: predictions = your_model.predict()
            
            # Simulated prediction data (replace with actual model output)
            import random
            aqi = random.randint(50, 150)
            pm25 = random.uniform(10, 50)
            pm10 = random.uniform(20, 80)
            co2 = random.uniform(350, 450)
            no2 = random.uniform(10, 40)
            
            send_prediction_data(aqi, pm25, pm10, co2, no2)
            
            # Wait 60 seconds before next prediction
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\nStopped monitoring")


if __name__ == "__main__":
    # Run example usage
    example_usage()
    
    # Uncomment below to run continuous monitoring
    # continuous_monitoring()
