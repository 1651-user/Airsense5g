import os
import json
import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Load the same env file as your MQTT script
load_dotenv("/home/sdas/mong3/am3.env")

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")        # e.g. "milesiteaqi"
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")  # e.g. "ambience3_data"

print("Connecting with:")
print("  URI :", MONGO_URI)
print("  DB  :", MONGO_DB)
print("  Coll:", MONGO_COLLECTION)

# MongoDB connection
client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

# Fetch data (excluding _id or converting it to string)
docs = list(collection.find({}))  # you can filter here if needed

print(f"Total documents found: {len(docs)}")

if not docs:
    print("No data found in this collection. Check that your MQTT script is writing here.")
    client.close()
    raise SystemExit

# Make _id JSON/Excel friendly
for d in docs:
    d["_id"] = str(d["_id"])

# ---------- Save to JSON ----------
json_file = "output.json"
with open(json_file, "w") as f:
    json.dump(docs, f, indent=2)
print(f"✅ JSON file saved as {json_file}")

# ---------- Convert to flat DataFrame & save to Excel ----------
df = pd.json_normalize(docs)   # handles nested JSON

excel_file = "output.xlsx"
df.to_excel(excel_file, index=False)
print(f"✅ Excel file saved successfully as {excel_file}")

client.close()