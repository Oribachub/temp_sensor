# Sensor Dashboard - Netlify Deployment

A beautiful, responsive sensor dashboard for monitoring temperature and humidity data. This project consists of a static frontend (deployed on Netlify) and a Flask backend API.

## 🚀 Quick Deploy to Netlify

### Option 1: Deploy from GitHub (Recommended)

1. **Fork/Clone this repository** to your GitHub account
2. **Go to [Netlify](https://netlify.com)** and sign up/login
3. **Click "New site from Git"**
4. **Choose GitHub** and select your repository
5. **Configure build settings:**
   - Build command: (leave empty - static site)
   - Publish directory: `.` (root directory)
6. **Click "Deploy site"**

### Option 2: Manual Deploy

1. **Download the files** from this repository
2. **Go to [Netlify](https://netlify.com)** and sign up/login
3. **Drag and drop** the folder containing `index.html` to the Netlify dashboard
4. **Your site will be deployed automatically**

## 🔧 Backend Setup

The frontend expects a Flask API running with these endpoints:

- `GET /data/24h` - Returns 24-hour temperature/humidity data
- `GET /data/7d` - Returns 7-day temperature/humidity data

### Deploy Backend API

You can deploy your Flask API to:
- **Heroku** (free tier available)
- **Railway** (free tier available)
- **Render** (free tier available)
- **PythonAnywhere** (free tier available)
- **Your own server**

### Example Backend Deployment (Heroku)

1. **Create a `requirements.txt`** file in your backend directory:
```
Flask==2.3.3
pandas==2.0.3
gunicorn==21.2.0
```

2. **Create a `Procfile`**:
```
web: gunicorn web_script:app
```

3. **Deploy to Heroku**:
```bash
heroku create your-sensor-api
git add .
git commit -m "Deploy sensor API"
git push heroku main
```

## 🌐 Configure API URL

Once deployed:

1. **Open your Netlify site**
2. **Enter your API URL** in the configuration section
3. **Click "Update"** to connect to your backend

Example API URLs:
- `https://your-sensor-api.herokuapp.com`
- `https://your-api.railway.app`
- `http://your-server-ip:5000` (if running locally)

## 📁 File Structure

```
├── index.html          # Main dashboard (deploy to Netlify)
├── netlify.toml        # Netlify configuration
├── README.md           # This file
└── web_script.py       # Flask backend (deploy separately)
```

## 🔒 CORS Configuration

If you encounter CORS errors, ensure your Flask backend has CORS enabled:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
```

Add `flask-cors==4.0.0` to your `requirements.txt`.

## 🎨 Features

- **Responsive Design** - Works on desktop, tablet, and mobile
- **Real-time Data** - Fetches live sensor data
- **Beautiful Charts** - Interactive temperature and humidity graphs
- **Configurable API** - Easy to switch between different backend URLs
- **Loading States** - Professional loading indicators
- **Error Handling** - Graceful error messages

## 🛠️ Customization

- **Colors**: Modify the CSS variables in the `<style>` section
- **Charts**: Adjust Chart.js options in the JavaScript
- **Layout**: Modify the HTML structure and CSS grid
- **API Endpoints**: Update the fetch URLs in the JavaScript

## 📱 Mobile Support

The dashboard is fully responsive and optimized for mobile devices with:
- Touch-friendly interface
- Optimized chart sizes
- Responsive grid layout
- Mobile-friendly typography

## 🔄 Auto-refresh

To add auto-refresh functionality, add this to the JavaScript:

```javascript
// Refresh data every 5 minutes
setInterval(loadData, 5 * 60 * 1000);
```

## 🚨 Troubleshooting

### Common Issues:

1. **CORS Errors**: Ensure your backend has CORS enabled
2. **API Not Found**: Check your API URL and ensure the backend is running
3. **Charts Not Loading**: Check browser console for JavaScript errors
4. **Data Not Showing**: Verify your API endpoints return the expected JSON format

### Debug Mode:

Open browser developer tools (F12) and check the Console tab for error messages and API call logs.

## 📄 License

This project is open source and available under the MIT License. 