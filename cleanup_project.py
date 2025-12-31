"""
Clean up AirSense 5G project - Remove unwanted files
"""
import os
import glob

print("Cleaning up AirSense 5G project...")
print("=" * 70)

# Files to remove (patterns)
files_to_remove = [
    # Old/obsolete Python scripts
    'excel_integration.py',
    'live_ai_system.py',
    'mqtt_to_phi2.py',
    'predict_with_excel_enhanced.py',
    'start_with_predictions.py',
    'train_models_mongodb.py',
    'mqtt_to_ai_sensor*.py',
    'json2excel*.py',
    'mqtt2mongo*.py',
    'train_multi_target_model.py',
    
    # Backup Excel files
    'output*_backup_*.xlsx',
    'output*_corrupted_*.xlsx',
    '*_backup_*.xlsx',
    
    # Test/debug scripts
    'test_*.py',
    'check_*.py',
    'debug_*.py',
    'discover_*.py',
    'verify_*.py',
    'show_*.py',
    'quick_*.py',
    
    # Fix scripts (no longer needed)
    'fix_*.py',
    'clean_*.py',
    'recreate_*.py',
    'restore_*.py',
    'apply_*.py',
    'force_*.py',
    'simple_*.py',
    
    # Send/update scripts (replaced by new system)
    'send_excel_*.py',
    'send_sample_*.py',
    'send_latest_*.py',
    'send_all_*.py',
    'update_*.py',
    'fast_update_*.py',
    
    # Old batch scripts
    'start_mqtt_*.bat',
    'start_mqtt_*.ps1',
    'start_all_5_sensors.bat',
    'start_all_sensors_live.bat',
    'start_backend.bat',
    'start_enhanced_system.bat',
    'start_live_system.bat',
    'start_system.bat',
    'start_ai_chat_system.bat',
    'setup_autostart.bat',
    'run_mqtt_*.bat',
    'run_mqtt_*.sh',
    'fix_ai_data.bat',
    
    # Old combined/merged Excel files
    'combined_sensor_data_*.xlsx',
    'mqtt_data_*.xlsx',
    'sensor_data_formatted.xlsx',
    
    # Temporary test files
    'output3_test.xlsx',
    
    # Old documentation (keeping only the latest)
    'AI_CHAT_*.md',
    'ALL_5_SENSORS_*.md',
    'ALL_SENSORS_*.md',
    'API_DOCUMENTATION_*.md',
    'AQI_ZERO_*.md',
    'BACKEND_URL_*.md',
    'COMPLETE_*.md',
    'CONNECTION_*.md',
    'CORRECTED_*.md',
    'DASHBOARD_*.md',
    'DATA_*.md',
    'ENHANCED_*.md',
    'EXCEL_*.md',
    'FAST_UPDATE_*.md',
    'FILES_INDEX.md',
    'FINAL_*.md',
    'FLUTTER_APP_*.md',
    'IMPLEMENTATION_SUMMARY.md',
    'INDEX.md',
    'ISSUE_*.md',
    'LIVE_*.md',
    'MISSING_*.md',
    'MODEL_*.md',
    'MQTT_*.md',
    'PHI2_*.md',
    'PROGRESS_*.md',
    'QUERY_*.md',
    'QUICKSTART_*.md',
    'QUICK_START.md',
    'SENSOR*.md',
    'SETUP_*.md',
    'SINGLE_*.md',
    'SYSTEM_ARCHITECTURE.txt',
    'SYSTEM_SETUP.md',
    'TROUBLESHOOTING.md',
    'VISUAL_SUMMARY.txt',
    
    # Backup JSON files
    'mqtt_data_sensor*_backup*.json',
    
    # Other temporary files
    'query',
    'env_template.txt',
]

# Keep these important files
keep_files = {
    # Core Python scripts
    'send_data_from_json.py',
    'live_system_json_based.py',
    
    # Backend
    'backend/server.py',
    
    # Batch scripts
    'START_SYSTEM.bat',
    'START_ALL.bat',
    
    # Documentation
    'README.md',
    'README_COMPLETE.md',
    'SYSTEM_READY.md',
    'STREAMLINED_FLOW.md',
    'IMPLEMENTATION_COMPLETE.md',
    'QUICK_REFERENCE.md',
    
    # Data files
    'output1.xlsx',
    'output2.xlsx',
    'output3.xlsx',
    'output4.xlsx',
    'output5.xlsx',
    'mqtt_data_sensor1.json',
    'mqtt_data_sensor2.json',
    'mqtt_data.json',
    'mqtt_data_sensor4.json',
    'mqtt_data_sensor5.json',
    
    # Config files
    '.env',
    'am3.env',
    'amb1.env',
    'amb2.env',
    'amb4.env',
    'amb5.env',
    
    # Models
    'models/',
    
    # Flutter app
    'lib/',
    'android/',
    'ios/',
    'web/',
    'windows/',
    'linux/',
    'macos/',
}

removed_count = 0
kept_count = 0

for pattern in files_to_remove:
    for file in glob.glob(pattern):
        # Skip if it's in the keep list
        if any(keep in file for keep in keep_files):
            continue
        
        try:
            if os.path.isfile(file):
                os.remove(file)
                print(f"  Removed: {file}")
                removed_count += 1
        except Exception as e:
            print(f"  Error removing {file}: {e}")

print("\n" + "=" * 70)
print(f"Cleanup complete!")
print(f"  Removed: {removed_count} files")
print(f"\nKept essential files:")
print("  - send_data_from_json.py")
print("  - live_system_json_based.py")
print("  - START_SYSTEM.bat")
print("  - backend/server.py")
print("  - All JSON data files")
print("  - All Excel output files")
print("  - Flutter app files")
print("  - Models directory")
print("  - Latest documentation")
