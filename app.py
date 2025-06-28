#!/usr/bin/env python3
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
from datetime import datetime, timedelta, timezone
import os

# === CONFIGURATION ===
LOG_FILE = 'sensor_log.csv'

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def load_dataframe():
    if not os.path.isfile(LOG_FILE):
        return pd.DataFrame(columns=['timestamp','temperature_C','humidity_pct'])
    df = pd.read_csv(LOG_FILE, parse_dates=['timestamp'])
    return df.set_index('timestamp')

def get_24h_data():
    df = load_dataframe()
    now = datetime.now(timezone.utc)
    window = df[now - timedelta(hours=24):now]
    window = window.resample('30T').mean().dropna()
    return [
        {'timestamp': ts.isoformat(),
         'temperature': row.temperature_C,
         'humidity': row.humidity_pct}
        for ts, row in window.iterrows()
    ]

def get_7d_data():
    df = load_dataframe()
    now = datetime.now(timezone.utc)
    window = df[now - timedelta(days=7):now]
    window = window.resample('2H').mean().dropna()
    return [
        {'timestamp': ts.isoformat(),
         'temperature': row.temperature_C,
         'humidity': row.humidity_pct}
        for ts, row in window.iterrows()
    ]

@app.route('/')
def index():
    return jsonify({
        'message': 'Sensor API is running',
        'endpoints': {
            '24h_data': '/data/24h',
            '7d_data': '/data/7d'
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