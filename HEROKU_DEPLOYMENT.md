# Deploying to Heroku

## Prerequisites
1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
2. Have a Heroku account (sign up at https://heroku.com)

## Deployment Steps

### 1. Install Heroku CLI
```bash
# macOS
brew tap heroku/brew && brew install heroku
```

### 2. Login to Heroku
```bash
heroku login
```

### 3. Create Heroku App
```bash
heroku create your-app-name
```

### 4. Add Buildpack (if needed)
```bash
heroku buildpacks:set heroku/python
```

### 5. Deploy
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### 6. Open Your App
```bash
heroku open
```

## Important Notes

### Environment Variables
Set your secret key:
```bash
heroku config:set SECRET_KEY=your-secret-key-here
```

### Database
- Heroku supports PostgreSQL (recommended for production)
- For SQLite (development), the database will be ephemeral

### Scaling
```bash
heroku ps:scale web=1
```

## Troubleshooting

### View Logs
```bash
heroku logs --tail
```

### Restart App
```bash
heroku restart
```

### Check Status
```bash
heroku ps
``` 