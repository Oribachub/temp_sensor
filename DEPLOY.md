# Simple Netlify Deployment

## Method 1: Drag & Drop (Easiest)

1. Go to [netlify.com](https://netlify.com)
2. Sign up/login
3. Drag the `index.html` file directly to the Netlify dashboard
4. Your site will be live instantly!

## Method 2: GitHub + Netlify

1. Create a new GitHub repository
2. Upload only the `index.html` file
3. Go to Netlify → "New site from Git"
4. Connect your GitHub repo
5. Deploy (no build settings needed)

## Method 3: Manual Upload

1. Go to Netlify dashboard
2. Click "New site from Git" → "Deploy manually"
3. Upload the `index.html` file
4. Deploy

## Troubleshooting

- **404 Error**: Make sure you're uploading `index.html` (not a folder)
- **Blank Page**: Check browser console for JavaScript errors
- **API Issues**: Update the API URL in the dashboard configuration

## After Deployment

1. Your site will be at `https://your-site-name.netlify.app`
2. Enter your Flask API URL in the configuration section
3. Click "Update" to connect to your backend 