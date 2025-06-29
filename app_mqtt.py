#!/usr/bin/env python3
"""
MQTT-enabled Flask API for Real-time Temperature Sensor Data
Subscribes to HiveMQ broker and serves data to frontend
"""

from flask import Flask, jsonify
from flask_cors import CORS
import paho.mqtt.client as mqtt
import json
import threading
import time
from datetime import datetime, timedelta
from collections import deque
import os

# === MQTT CONFIGURATION ===
MQTT_BROKER = "6764752d2a144637b3706fb478c5f216.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_TOPIC = "temp_sensor/readings"
MQTT_USERNAME = "cursor"  # Replace with your HiveMQ username
MQTT_PASSWORD = "cur1234S$"  # Replace with your HiveMQ password

# === DATA STORAGE ===
# Store recent readings in memory (last 1000 readings)
recent_readings = deque(maxlen=1000)
latest_reading = None

# === MQTT CLIENT SETUP ===
def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    if rc == 0:
        print(f"✅ Backend connected to MQTT broker: {MQTT_BROKER}")
        # Subscribe to the topic
        client.subscribe(MQTT_TOPIC)
        print(f"📡 Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"❌ Failed to connect to MQTT broker, return code: {rc}")

def on_message(client, userdata, msg):
    """Callback when message is received from MQTT broker"""
    global latest_reading, recent_readings
    
    try:
        # Parse JSON message
        payload = json.loads(msg.payload.decode())
        
        # Convert timestamp string to datetime object
        timestamp_str = payload['timestamp']
        if '+00:00' in timestamp_str:
            # UTC timestamp - convert to local
            timestamp = datetime.fromisoformat(timestamp_str.replace('+00:00', '+00:00')).replace(tzinfo=None)
        else:
            # Local timestamp
            timestamp = datetime.fromisoformat(timestamp_str)
        
        # Create reading object
        reading = {
            'timestamp': timestamp,
            'temperature': payload['temperature'],
            'humidity': payload['humidity'],
            'status': payload['status'],
            'error': payload['error']
        }
        
        # Update latest reading
        latest_reading = reading
        
        # Add to recent readings
        recent_readings.append(reading)
        
        print(f"📥 Received: {reading['temperature']}°C, {reading['humidity']}% RH at {timestamp}")
        
    except Exception as e:
        print(f"❌ Error processing MQTT message: {e}")

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
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect

# Enable TLS/SSL
mqtt_client.tls_set()

# === FLASK APP ===
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def get_readings_in_timerange(hours):
    """Get readings from the last N hours"""
    if not recent_readings:
        return []
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    # Filter readings within time range
    filtered_readings = [
        reading for reading in recent_readings
        if reading['timestamp'] >= cutoff_time
    ]
    
    return filtered_readings

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        "message": "MQTT Temperature Sensor API",
        "status": "running",
        "mqtt_broker": MQTT_BROKER,
        "topic": MQTT_TOPIC,
        "latest_reading": latest_reading['timestamp'].isoformat() if latest_reading else None
    })

@app.route('/data/latest')
def get_latest():
    """Get the latest sensor reading"""
    if not latest_reading:
        return jsonify({"error": "No data available"}), 404
    
    return jsonify({
        "timestamp": latest_reading['timestamp'].isoformat(),
        "temperature": latest_reading['temperature'],
        "humidity": latest_reading['humidity'],
        "status": latest_reading['status']
    })

@app.route('/data/24h')
def get_24h_data():
    """Get data from the last 24 hours"""
    readings = get_readings_in_timerange(24)
    
    if not readings:
        return jsonify([])
    
    # Format data for frontend
    formatted_data = []
    for reading in readings:
        formatted_data.append({
            "timestamp": reading['timestamp'].isoformat(),
            "temperature": reading['temperature'],
            "humidity": reading['humidity']
        })
    
    return jsonify(formatted_data)

@app.route('/data/7d')
def get_7d_data():
    """Get data from the last 7 days"""
    readings = get_readings_in_timerange(24 * 7)
    
    if not readings:
        return jsonify([])
    
    # Format data for frontend
    formatted_data = []
    for reading in readings:
        formatted_data.append({
            "timestamp": reading['timestamp'].isoformat(),
            "temperature": reading['temperature'],
            "humidity": reading['humidity']
        })
    
    return jsonify(formatted_data)

@app.route('/status')
def get_status():
    """Get API and MQTT status"""
    mqtt_connected = mqtt_client.is_connected()
    
    return jsonify({
        "api_status": "running",
        "mqtt_connected": mqtt_connected,
        "mqtt_broker": MQTT_BROKER,
        "total_readings": len(recent_readings),
        "latest_reading": latest_reading['timestamp'].isoformat() if latest_reading else None
    })

def start_mqtt_client():
    """Start MQTT client in a separate thread"""
    try:
        print(f"🔌 Connecting to MQTT broker: {MQTT_BROKER}:{MQTT_PORT}")
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_forever()
    except Exception as e:
        print(f"❌ MQTT connection error: {e}")

if __name__ == '__main__':
    # Start MQTT client in background thread
    mqtt_thread = threading.Thread(target=start_mqtt_client, daemon=True)
    mqtt_thread.start()
    
    # Wait a moment for MQTT connection
    time.sleep(3)
    
    print("🚀 Starting MQTT-enabled Flask API...")
    print(f"📡 MQTT Broker: {MQTT_BROKER}")
    print(f"📋 Topic: {MQTT_TOPIC}")
    print("🌐 API will be available at http://localhost:5000")
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=False) 