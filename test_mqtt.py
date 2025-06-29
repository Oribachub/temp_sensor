#!/usr/bin/env python3
"""
Simple MQTT connection test for HiveMQ
"""

import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime

# === MQTT CONFIGURATION ===
MQTT_BROKER = "6764752d2a144637b3706fb478c5f216.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_TOPIC = "temp_sensor/test"
MQTT_USERNAME = "cursor"  # Replace with your HiveMQ username
MQTT_PASSWORD = "cur1234S$"  # Replace with your HiveMQ password

def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    if rc == 0:
        print(f"✅ Successfully connected to MQTT broker: {MQTT_BROKER}")
        print(f"📡 Connection return code: {rc}")
    else:
        print(f"❌ Failed to connect to MQTT broker, return code: {rc}")

def on_publish(client, userdata, mid):
    """Callback when message is published"""
    print(f"📤 Test message published successfully (ID: {mid})")

def on_disconnect(client, userdata, rc):
    """Callback when disconnected from MQTT broker"""
    if rc != 0:
        print(f"⚠️ Unexpected disconnection (RC: {rc})")
    else:
        print("🔌 Disconnected from MQTT broker")

def test_mqtt_connection():
    """Test MQTT connection and publish a test message"""
    print("🧪 Testing MQTT connection to HiveMQ...")
    print(f"📡 Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"👤 Username: {MQTT_USERNAME}")
    
    # Initialize MQTT client
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    
    # Enable TLS/SSL
    client.tls_set()
    
    try:
        # Connect to broker
        print("🔌 Connecting to MQTT broker...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        # Start the loop
        client.loop_start()
        
        # Wait for connection
        time.sleep(3)
        
        if client.is_connected():
            # Publish test message
            test_message = {
                "timestamp": datetime.now().isoformat(),
                "test": True,
                "message": "MQTT connection test successful"
            }
            
            result = client.publish(MQTT_TOPIC, json.dumps(test_message), qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print("✅ Test message sent successfully!")
                print(f"📋 Topic: {MQTT_TOPIC}")
                print(f"📄 Message: {json.dumps(test_message, indent=2)}")
            else:
                print(f"❌ Failed to publish test message: {result.rc}")
        else:
            print("❌ Not connected to MQTT broker")
        
        # Wait a moment then disconnect
        time.sleep(2)
        client.loop_stop()
        client.disconnect()
        
    except Exception as e:
        print(f"❌ Error during MQTT test: {e}")

if __name__ == "__main__":
    test_mqtt_connection() 