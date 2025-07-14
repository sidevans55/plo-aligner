# Deploying to Render.com

## Prerequisites
1. Create a Render account: https://render.com (Free!)
2. Connect your GitHub account to Render

## Deployment Steps

### 1. Push to GitHub
First, make sure your code is on GitHub:
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2. Deploy on Render
1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → **"Web Service"**
3. **Connect your GitHub repository**
4. **Configure the service**:
   - **Name**: `plo-platform`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: `Free`

### 3. Environment Variables
Add these in Render dashboard:
- `SECRET_KEY`: Generate a random string
- `PYTHON_VERSION`: `3.11.7`

### 4. Deploy
Click **"Create Web Service"** and wait for deployment!

## Your App URL
Render will give you a URL like: `https://plo-platform.onrender.com`

## Important Notes

### Free Tier Limitations
- App sleeps after 15 minutes of inactivity
- Takes ~30 seconds to wake up
- 750 hours/month free

### Database
- SQLite works but data is ephemeral
- For production, consider PostgreSQL

### Custom Domain
- Free tier includes custom domains
- Add in Render dashboard

## Troubleshooting

### View Logs
- Go to your service in Render dashboard
- Click "Logs" tab

### Restart Service
- Go to your service
- Click "Manual Deploy" → "Deploy latest commit"

### Check Status
- Service status shown in dashboard
- Green = running, Yellow = building, Red = error 