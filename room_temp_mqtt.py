#!/usr/bin/env python3
"""
MQTT-enabled Temperature and Humidity Sensor Bot
Publishes sensor data to HiveMQ broker for real-time updates
"""

import adafruit_dht
import board
import time
import json
import paho.mqtt.client as mqtt
import schedule
from datetime import datetime
import os

# === MQTT CONFIGURATION ===
MQTT_BROKER = "6764752d2a144637b3706fb478c5f216.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_TOPIC = "temp_sensor/readings"
MQTT_USERNAME = "cursor"  # Replace with your HiveMQ username
MQTT_PASSWORD = "cur1234S$"  # Replace with your HiveMQ password

# === SENSOR CONFIGURATION ===
SEND_INTERVAL_MINUTES = 1  # Interval for sensor readings (in minutes)
DHT_PIN = board.D26  # GPIO pin for DHT11 sensor

# === MQTT CLIENT SETUP ===
def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    if rc == 0:
        print(f"✅ Connected to MQTT broker: {MQTT_BROKER}")
    else:
        print(f"❌ Failed to connect to MQTT broker, return code: {rc}")

def on_publish(client, userdata, mid):
    """Callback when message is published"""
    print(f"📤 Message published successfully (ID: {mid})")

def on_disconnect(client, userdata, rc):
    """Callback when disconnected from MQTT broker"""
    if rc != 0:
        print(f"⚠️ Unexpected disconnection from MQTT broker (RC: {rc})")
    else:
        print("🔌 Disconnected from MQTT broker")

# Initialize MQTT client
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
mqtt_client.on_connect = on_connect
mqtt_client.on_publish = on_publish
mqtt_client.on_disconnect = on_disconnect

# Enable TLS/SSL
mqtt_client.tls_set()

# Initialize DHT sensor
dht = adafruit_dht.DHT11(DHT_PIN)

def read_sensor():
    """Read temperature and humidity from DHT11 sensor"""
    try:
        temperature = dht.temperature
        humidity = dht.humidity
        
        if temperature is not None and humidity is not None:
            return temperature, humidity, "OK", ""
        else:
            return None, None, "ERROR", "Failed to read sensor"
            
    except Exception as e:
        return None, None, "ERROR", str(e)

def publish_reading(temperature, humidity, status="OK", error_msg=""):
    """Publish sensor reading to MQTT broker"""
    try:
        # Create message payload
        timestamp = datetime.now().isoformat()
        payload = {
            "timestamp": timestamp,
            "temperature": round(temperature, 1) if temperature else None,
            "humidity": round(humidity, 1) if humidity else None,
            "status": status,
            "error": error_msg
        }
        
        # Convert to JSON
        message = json.dumps(payload)
        
        # Publish to MQTT broker
        result = mqtt_client.publish(MQTT_TOPIC, message, qos=1)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"📊 Published: {temperature}°C, {humidity}% RH")
            return True
        else:
            print(f"❌ Failed to publish: {result.rc}")
            return False
            
    except Exception as e:
        print(f"❌ Error publishing to MQTT: {e}")
        return False

def send_sensor_data():
    """Main function to read sensor and publish data"""
    print(f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Reading sensor...")
    
    # Read sensor
    temperature, humidity, status, error_msg = read_sensor()
    
    if temperature is not None and humidity is not None:
        # Publish to MQTT
        success = publish_reading(temperature, humidity, status, error_msg)
        
        if success:
            print(f"✅ Data published successfully")
        else:
            print(f"❌ Failed to publish data")
    else:
        print(f"❌ Sensor read failed: {error_msg}")

def main():
    """Main function"""
    print("🚀 MQTT Temperature Sensor Bot Starting...")
    print(f"📡 Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"📋 Topic: {MQTT_TOPIC}")
    print(f"⏱️  Interval: {SEND_INTERVAL_MINUTES} minute(s)")
    
    # Connect to MQTT broker
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
        
        # Wait for connection
        time.sleep(2)
        
        # Schedule sensor readings
        schedule.every(SEND_INTERVAL_MINUTES).minutes.do(send_sensor_data)
        
        # Send initial reading
        send_sensor_data()
        
        print(f"✅ Bot started successfully! Sending data every {SEND_INTERVAL_MINUTES} minute(s)")
        print("Press Ctrl+C to stop")
        
        # Main loop
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping bot...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print("🔌 Disconnected from MQTT broker")

if __name__ == "__main__":
    main() 