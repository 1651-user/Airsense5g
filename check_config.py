"""Check backend configuration"""
import os
from dotenv import load_dotenv

# Load .env from backend folder
load_dotenv('backend/.env')

print("=" * 60)
print("BACKEND CONFIGURATION")
print("=" * 60)
print(f"LM_STUDIO_BASE_URL: {os.getenv('LM_STUDIO_BASE_URL', 'NOT SET (default: http://localhost:1234/v1)')}")
print(f"FLASK_HOST: {os.getenv('FLASK_HOST', 'NOT SET (default: 0.0.0.0)')}")
print(f"FLASK_PORT: {os.getenv('FLASK_PORT', 'NOT SET (default: 5000)')}")
print("=" * 60)
