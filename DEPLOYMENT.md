# Deploying to Vercel

## Prerequisites
1. Install Vercel CLI: `npm i -g vercel`
2. Have a Vercel account (sign up at https://vercel.com)

## Deployment Steps

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Deploy
```bash
vercel
```

### 4. Follow the prompts:
- Set up and deploy? → `Y`
- Which scope? → Select your account
- Link to existing project? → `N`
- What's your project's name? → `plo-platform` (or any name)
- In which directory is your code located? → `./` (current directory)
- Want to override the settings? → `N`

### 5. Your app will be deployed!
Vercel will give you a URL like: `https://your-app-name.vercel.app`

## Important Notes

### Database
- Vercel uses serverless functions, so SQLite won't work
- Consider using:
  - Vercel Postgres
  - PlanetScale
  - Supabase
  - Or any cloud database

### Environment Variables
Set these in your Vercel dashboard:
- `SECRET_KEY`: Your Flask secret key
- `DATABASE_URL`: Your database connection string

### File Uploads
- Vercel has a 4.5MB limit for serverless functions
- Consider using:
  - AWS S3
  - Cloudinary
  - Or process files client-side

## Alternative: Railway Deployment
If you prefer Railway (which supports SQLite):

1. Go to https://railway.app
2. Connect your GitHub repository
3. Railway will auto-detect and deploy your Flask app
4. Add environment variables in Railway dashboard

## Local Testing
Before deploying, test locally:
```bash
python3 app.py
```
Visit: http://localhost:5000 