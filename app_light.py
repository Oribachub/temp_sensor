#!/usr/bin/env python3
from flask import Flask, jsonify
from flask_cors import CORS
import csv
from datetime import datetime, timedelta
import os
from collections import defaultdict

# === CONFIGURATION ===
LOG_FILE = 'sensor_log.csv'

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def load_data():
    """Load data from CSV without pandas"""
    if not os.path.isfile(LOG_FILE):
        print(f"CSV file not found: {LOG_FILE}")
        return []
    
    data = []
    try:
        with open(LOG_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Handle both UTC and local timestamps
                    timestamp_str = row['timestamp']
                    if '+00:00' in timestamp_str:
                        # UTC timestamp - convert to local
                        timestamp = datetime.fromisoformat(timestamp_str.replace('+00:00', '+00:00')).replace(tzinfo=None)
                    else:
                        # Local timestamp
                        timestamp = datetime.fromisoformat(timestamp_str)
                    
                    temperature = float(row['temperature_C'])
                    humidity = float(row['humidity_pct'])
                    data.append({
                        'timestamp': timestamp,
                        'temperature': temperature,
                        'humidity': humidity
                    })
                except (ValueError, KeyError) as e:
                    print(f"Error parsing row: {e}")
                    continue  # Skip invalid rows
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return []
    
    sorted_data = sorted(data, key=lambda x: x['timestamp'])
    print(f"Loaded {len(sorted_data)} data points")
    if sorted_data:
        print(f"Latest timestamp: {sorted_data[-1]['timestamp']}")
        print(f"Earliest timestamp: {sorted_data[0]['timestamp']}")
    
    return sorted_data

def resample_data(data, interval_minutes):
    """Simple resampling without pandas"""
    if not data:
        return []
    
    # Group data by time intervals
    grouped = defaultdict(list)
    for item in data:
        # Round timestamp to nearest interval
        timestamp = item['timestamp']
        rounded = timestamp.replace(second=0, microsecond=0)
        rounded = rounded.replace(minute=(rounded.minute // interval_minutes) * interval_minutes)
        grouped[rounded].append(item)
    
    # Calculate averages for each group
    result = []
    for timestamp, items in sorted(grouped.items()):
        if items:
            avg_temp = sum(item['temperature'] for item in items) / len(items)
            avg_humidity = sum(item['humidity'] for item in items) / len(items)
            result.append({
                'timestamp': timestamp.isoformat(),
                'temperature': round(avg_temp, 2),
                'humidity': round(avg_humidity, 2)
            })
    
    return result

def get_24h_data():
    """Get last 24 hours of data, resampled to 30-minute intervals"""
    data = load_data()
    now = datetime.now()
    cutoff = now - timedelta(hours=24)
    
    # Filter last 24 hours
    recent_data = [item for item in data if item['timestamp'] >= cutoff]
    
    # Resample to 30-minute intervals
    return resample_data(recent_data, 30)

def get_7d_data():
    """Get last 7 days of data, resampled to 2-hour intervals"""
    data = load_data()
    now = datetime.now()
    cutoff = now - timedelta(days=7)
    
    # Filter last 7 days
    recent_data = [item for item in data if item['timestamp'] >= cutoff]
    
    # Resample to 2-hour intervals
    return resample_data(recent_data, 120)

@app.route('/debug')
def debug():
    """Debug endpoint to see what data is being loaded"""
    data = load_data()
    if not data:
        return jsonify({"error": "No data loaded", "csv_exists": os.path.isfile(LOG_FILE)})
    
    latest = data[-1] if data else None
    earliest = data[0] if data else None
    
    return jsonify({
        "total_entries": len(data),
        "latest_entry": {
            "timestamp": latest['timestamp'].isoformat() if latest else None,
            "temperature": latest['temperature'] if latest else None,
            "humidity": latest['humidity'] if latest else None
        },
        "earliest_entry": {
            "timestamp": earliest['timestamp'].isoformat() if earliest else None,
            "temperature": earliest['temperature'] if earliest else None,
            "humidity": earliest['humidity'] if earliest else None
        },
        "csv_file_size": os.path.getsize(LOG_FILE) if os.path.isfile(LOG_FILE) else 0
    })

@app.route('/')
def index():
    return jsonify({
        'message': 'Sensor API is running',
        'endpoints': {
            '24h_data': '/data/24h',
            '7d_data': '/data/7d',
            'debug': '/debug'
        }
    })

@app.route('/data/24h')
def data_24h():
    return jsonify(get_24h_data())

@app.route('/data/7d')
def data_7d():
    return jsonify(get_7d_data())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 