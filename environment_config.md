# Environment Variables Configuration

## Required Environment Variables

### For Render Deployment:

1. **SECRET_KEY**
   - **Purpose**: Flask session security and CSRF protection
   - **Value**: Generate a random string (32+ characters)
   - **Example**: `my-super-secret-key-12345-change-this`

2. **FLASK_ENV**
   - **Purpose**: Set Flask environment
   - **Value**: `production`
   - **Example**: `production`

3. **FLASK_DEBUG**
   - **Purpose**: Disable debug mode in production
   - **Value**: `False`
   - **Example**: `False`

## How to Set Environment Variables in Render:

1. Go to your Render service dashboard
2. Click on "Environment" tab
3. Add each variable:
   - **Key**: `SECRET_KEY`
   - **Value**: `your-generated-secret-key-here`
   - Click "Save Changes"

## Generating a Secure SECRET_KEY:

You can generate a secure key using Python:
```python
import secrets
print(secrets.token_hex(32))
```

## Optional Environment Variables:

- **DATABASE_URL**: If you want to use PostgreSQL instead of SQLite
- **UPLOAD_FOLDER**: Custom upload directory path
- **MAX_CONTENT_LENGTH**: Maximum file upload size

## Security Notes:

- Never commit your actual SECRET_KEY to Git
- Use different keys for development and production
- Keep your .env file in .gitignore 