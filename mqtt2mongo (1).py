import os
import json
import logging
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# -----------------------------
# Logging setup
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)  # FIXED: __name__ instead of _name_

# -----------------------------
# Load environment variables
# -----------------------------
dotenv_loaded = load_dotenv("/home/sdas/mong3/am3.env")

if not dotenv_loaded:
    logger.warning("⚠ .env file not found or could not be loaded!")

# MQTT settings
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

# MongoDB settings
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

logger.info(f"MQTT_BROKER: {MQTT_BROKER}")
logger.info(f"MQTT_PORT: {MQTT_PORT}")
logger.info(f"MQTT_TOPIC: {MQTT_TOPIC}")
logger.info(f"MONGO_DB: {MONGO_DB}")
logger.info(f"MONGO_COLLECTION: {MONGO_COLLECTION}")

if not all([MQTT_BROKER, MQTT_TOPIC, MONGO_URI, MONGO_DB, MONGO_COLLECTION]):
    logger.warning("⚠ Some environment variables are missing. Check your .env file.")

# -----------------------------
# MongoDB client
# -----------------------------
mongo_client = MongoClient(MONGO_URI, server_api=ServerApi('1'))

def ping_mongodb_server() -> bool:
    try:
        mongo_client.admin.command('ping')
        logger.info("✅ Successfully connected to MongoDB!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        return False

db = mongo_client[MONGO_DB]
collection = db[MONGO_COLLECTION]
logger.info(f"Using collection: {collection.full_name}")

# -----------------------------
# MQTT callbacks (Callback API v2)
# -----------------------------
def on_connect(client, userdata, flags, reason_code, properties=None):
    """
    Callback for when the client receives a CONNACK response from the server.
    Signature for CallbackAPIVersion.VERSION2.
    """
    logger.info(f"on_connect called, reason_code={reason_code}")

    # For both MQTT v3 and v5, reason_code == 0 means success.
    if reason_code == 0:
        logger.info("✅ Connected to MQTT broker")
        result, mid = client.subscribe(MQTT_TOPIC)
        if result == mqtt.MQTT_ERR_SUCCESS:
            logger.info(f"✅ Subscribed to topic: {MQTT_TOPIC}")
        else:
            logger.error(f"❌ Failed to subscribe to topic {MQTT_TOPIC}, result code: {result}")
    else:
        logger.error(f"❌ Failed to connect to MQTT broker, reason_code={reason_code}")

def on_message(client, userdata, msg):
    """
    Callback for when a PUBLISH message is received from the server.
    """
    raw_payload = msg.payload.decode("utf-8", errors="ignore")
    logger.info(f"📩 Message received on topic '{msg.topic}' (QoS={msg.qos}): {raw_payload}")

    # Try to parse JSON, but handle non-JSON payloads gracefully
    try:
        message = json.loads(raw_payload)
        logger.info("✅ Payload parsed as JSON")
    except json.JSONDecodeError:
        logger.warning("⚠ Payload is not valid JSON. Storing raw payload instead.")
        message = {
            "raw_payload": raw_payload,
            "topic": msg.topic,
            "qos": msg.qos
        }

    try:
        insert_result = collection.insert_one(message)
        logger.info(f"✅ Document inserted into MongoDB with _id={insert_result.inserted_id}")
    except Exception as e:
        logger.error(f"❌ Error inserting message into MongoDB: {e}", exc_info=True)

# -----------------------------
# MQTT client setup
# -----------------------------
def setup_mqtt_client() -> mqtt.Client:
    # Use Callback API VERSION2 → no DeprecationWarning
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_message = on_message

    return client

# -----------------------------
# Main
# -----------------------------
def main():
    if not ping_mongodb_server():
        logger.error("Stopping because MongoDB connection failed.")
        return

    mqtt_client = setup_mqtt_client()

    try:
        logger.info(f"Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT} ...")
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    except Exception as e:
        logger.error(f"❌ Failed to connect to MQTT broker: {e}")
        return

    try:
        logger.info("Starting MQTT loop_forever()")
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt: MQTT client disconnecting...")
        mqtt_client.disconnect()
    finally:
        mongo_client.close()
        logger.info("MongoDB client closed.")

if __name__ == "__main__":   # FIXED: __name__ / __main__
    main()