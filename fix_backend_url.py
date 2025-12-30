"""Update backend .env file with correct Phi-2 IP address"""
import os

env_path = 'backend/.env'

# Read current .env
with open(env_path, 'r') as f:
    content = f.read()

# Replace the old IP with the correct one
old_ip = '192.168.1.147'
new_ip = '192.168.0.103'

updated_content = content.replace(old_ip, new_ip)

# Write back
with open(env_path, 'w') as f:
    f.write(updated_content)

print("=" * 60)
print("UPDATED BACKEND CONFIGURATION")
print("=" * 60)
print(f"Changed: http://{old_ip}:1234/v1")
print(f"To:      http://{new_ip}:1234/v1")
print("=" * 60)
print()
print("✓ Configuration updated!")
print()
print("NEXT STEP: Restart the backend server:")
print("  1. Press CTRL+C in the backend terminal")
print("  2. Run: python backend/server.py")
print()
