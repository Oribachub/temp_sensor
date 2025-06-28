#!/usr/bin/env python3
from flask import Flask, render_template_string, jsonify, url_for
from flask_cors import CORS
import pandas as pd
from datetime import datetime, timedelta, timezone
import os

# === CONFIGURATION ===
LOG_FILE = 'sensor_log.csv'
HOST     = '0.0.0.0'
PORT     = 5000

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sensor Dashboard</title>

  <!-- load from local static/js folder -->
  <script src="{{ url_for('static', filename='js/chart.umd.min.js') }}"></script>
  <script src="{{ url_for('static', filename='js/moment.min.js') }}"></script>
  <script src="{{ url_for('static', filename='js/chartjs-adapter-moment.min.js') }}"></script>

  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 20px;
      color: #333;
    }

    .container {
      max-width: 1200px;
      margin: 0 auto;
    }

    .header {
      text-align: center;
      margin-bottom: 40px;
      color: white;
    }

    .header h1 {
      font-size: 2.5rem;
      font-weight: 300;
      margin-bottom: 10px;
      text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }

    .header p {
      font-size: 1.1rem;
      opacity: 0.9;
      font-weight: 300;
    }

    .chart-grid {
      display: grid;
      gap: 30px;
      margin-bottom: 30px;
    }

    .chart-card {
      background: white;
      border-radius: 15px;
      padding: 25px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.1);
      transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .chart-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }

    .chart-card h2 {
      font-size: 1.4rem;
      font-weight: 600;
      margin-bottom: 20px;
      color: #2c3e50;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .chart-card h2::before {
      content: '';
      width: 4px;
      height: 20px;
      background: linear-gradient(45deg, #667eea, #764ba2);
      border-radius: 2px;
    }

    .chart-container {
      position: relative;
      height: 350px;
      margin-bottom: 10px;
    }

    .loading {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(255, 255, 255, 0.9);
      color: #666;
      font-style: italic;
      z-index: 10;
    }

    .loading.hidden {
      display: none;
    }

    .error {
      background: #fee;
      border: 1px solid #fcc;
      border-radius: 8px;
      padding: 15px;
      margin: 20px 0;
      color: #c33;
      text-align: center;
    }

    .no-data {
      text-align: center;
      padding: 40px 20px;
      color: #666;
      font-style: italic;
    }

    .stats-bar {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }

    .stat-card {
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(10px);
      border-radius: 12px;
      padding: 20px;
      text-align: center;
      color: white;
      border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .stat-value {
      font-size: 2rem;
      font-weight: 600;
      margin-bottom: 5px;
    }

    .stat-label {
      font-size: 0.9rem;
      opacity: 0.8;
      text-transform: uppercase;
      letter-spacing: 1px;
    }

    @media (max-width: 768px) {
      .header h1 {
        font-size: 2rem;
      }
      
      .chart-card {
        padding: 20px;
      }
      
      .chart-container {
        height: 250px;
      }
      
      .stats-bar {
        grid-template-columns: 1fr;
      }
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
      width: 8px;
    }

    ::-webkit-scrollbar-track {
      background: rgba(255, 255, 255, 0.1);
      border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.3);
      border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
      background: rgba(255, 255, 255, 0.5);
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🌡️ Sensor Dashboard</h1>
      <p>Real-time temperature and humidity monitoring</p>
    </div>

    <div class="stats-bar" id="statsBar">
      <div class="stat-card">
        <div class="stat-value" id="currentTemp">--</div>
        <div class="stat-label">Current Temperature</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" id="currentHumidity">--</div>
        <div class="stat-label">Current Humidity</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" id="lastUpdate">--</div>
        <div class="stat-label">Last Update</div>
      </div>
    </div>

    <div class="chart-grid">
      <div class="chart-card">
        <h2>📊 Last 24 Hours</h2>
        <div class="chart-container">
          <div class="loading" id="loading24">Loading 24-hour data...</div>
          <canvas id="chart24"></canvas>
        </div>
      </div>

      <div class="chart-card">
        <h2>📈 Last 7 Days</h2>
        <div class="chart-container">
          <div class="loading" id="loading7">Loading 7-day data...</div>
          <canvas id="chart7"></canvas>
        </div>
      </div>
    </div>
  </div>

  <script>
    async function fetchData(endpoint) {
      const resp = await fetch(endpoint);
      if (!resp.ok) throw new Error(resp.statusText);
      return resp.json();
    }

    function updateStats(data) {
      if (data && data.length > 0) {
        const latest = data[data.length - 1];
        document.getElementById('currentTemp').textContent = latest.temperature.toFixed(1) + '°C';
        document.getElementById('currentHumidity').textContent = latest.humidity.toFixed(1) + '%';
        document.getElementById('lastUpdate').textContent = moment(latest.timestamp).format('HH:mm');
      }
    }

    function makeChart(ctx, data, unit) {
      if (!data.length) {
        // Hide the canvas and show no data message
        ctx.canvas.style.display = 'none';
        const noDataDiv = document.createElement('div');
        noDataDiv.className = 'no-data';
        noDataDiv.textContent = 'No data available for this time period.';
        ctx.canvas.parentNode.appendChild(noDataDiv);
        return;
      }

      const gradient1 = ctx.createLinearGradient(0, 0, 0, 400);
      gradient1.addColorStop(0, 'rgba(255, 99, 132, 0.2)');
      gradient1.addColorStop(1, 'rgba(255, 99, 132, 0)');

      const gradient2 = ctx.createLinearGradient(0, 0, 0, 400);
      gradient2.addColorStop(0, 'rgba(54, 162, 235, 0.2)');
      gradient2.addColorStop(1, 'rgba(54, 162, 235, 0)');

      new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.map(d => moment(d.timestamp)),
          datasets: [{
            label: 'Temperature (°C)',
            data: data.map(d => d.temperature),
            borderColor: '#ff6384',
            backgroundColor: gradient1,
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            yAxisID: 'y1',
            pointRadius: 4,
            pointHoverRadius: 6
          },{
            label: 'Humidity (%)',
            data: data.map(d => d.humidity),
            borderColor: '#36a2eb',
            backgroundColor: gradient2,
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            yAxisID: 'y2',
            pointRadius: 4,
            pointHoverRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            intersect: false,
            mode: 'index'
          },
          plugins: {
            legend: {
              position: 'top',
              labels: {
                usePointStyle: true,
                padding: 20,
                font: {
                  size: 12,
                  weight: '600'
                }
              }
            },
            tooltip: {
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              titleColor: '#fff',
              bodyColor: '#fff',
              borderColor: 'rgba(255, 255, 255, 0.1)',
              borderWidth: 1,
              cornerRadius: 8,
              displayColors: true
            }
          },
          scales: {
            x: {
              type: 'time',
              time: { 
                unit: unit, 
                tooltipFormat: 'MMM d, HH:mm',
                displayFormats: {
                  hour: 'HH:mm',
                  day: 'MMM d'
                }
              },
              title: { 
                display: true, 
                text: 'Time',
                font: { weight: '600' }
              },
              grid: {
                color: 'rgba(0, 0, 0, 0.1)'
              }
            },
            y1: {
              position: 'left',
              title: { 
                display: true, 
                text: 'Temperature (°C)',
                font: { weight: '600' }
              },
              grid: {
                color: 'rgba(0, 0, 0, 0.1)'
              }
            },
            y2: {
              position: 'right',
              title: { 
                display: true, 
                text: 'Humidity (%)',
                font: { weight: '600' }
              },
              grid: {
                drawOnChartArea: false,
                color: 'rgba(0, 0, 0, 0.1)'
              }
            }
          }
        }
      });
    }

    document.addEventListener('DOMContentLoaded', async () => {
      try {
        // Show loading state
        document.getElementById('loading24').classList.remove('hidden');
        document.getElementById('loading7').classList.remove('hidden');

        const data24 = await fetchData('/data/24h');
        const data7 = await fetchData('/data/7d');

        // Update stats with latest data
        updateStats(data24);

        // Create charts
        const ctx24 = document.getElementById('chart24').getContext('2d');
        makeChart(ctx24, data24, 'hour');

        const ctx7 = document.getElementById('chart7').getContext('2d');
        makeChart(ctx7, data7, 'day');

      } catch (e) {
        document.body.insertAdjacentHTML(
          'beforeend',
          `<div class="error">Error loading charts: ${e.message}</div>`
        );
      } finally {
        // Hide loading state
        document.getElementById('loading24').classList.add('hidden');
        document.getElementById('loading7').classList.add('hidden');
      }
    });
  </script>
</body>
</html>
"""

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
    return render_template_string(HTML)

@app.route('/data/24h')
def data_24h():
    return jsonify(get_24h_data())

@app.route('/data/7d')
def data_7d():
    return jsonify(get_7d_data())

if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
