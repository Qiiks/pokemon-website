# Deployment Guide

## 🚀 Local Development

### Prerequisites
- Python 3.8+ installed
- Modern web browser

### Steps
1. Install dependencies: `pip install -r requirements.txt`
2. Run the backend server: `python app.py`
3. Open `index.html` in your browser
4. The API will be available at `http://localhost:8080`

## 🌐 Production Deployment

### Option 1: Heroku Deployment
1. Create a Heroku account and install the CLI
2. Create a `Procfile` with: `web: python app.py`
3. Deploy using Git: `git push heroku main`

### Option 2: Vercel/Netlify (Static Frontend + Separate Backend)
1. Deploy backend to a service like PythonAnywhere or Heroku
2. Update `CONFIG.API.getBaseUrl()` in `config.js` to return your backend URL
3. Deploy frontend files to Vercel/Netlify

### Option 3: Traditional Hosting
1. Upload files to your web server
2. Ensure Python 3.8+ is installed
3. Run `python app.py` as a background service
4. Configure reverse proxy if needed

## ⚙️ Configuration

### API URL Configuration

The application automatically detects the environment:
- **Development**: Uses `http://localhost:8080` when running locally
- **Production**: Uses relative URLs (same domain) when deployed

To manually configure the API URL, edit `config.js`:

```javascript
// For custom backend URL (e.g., deployed to Heroku)
return 'https://your-backend.herokuapp.com';

// For same-domain deployment
return ''; // Empty string uses current domain
```

### Environment Variables (Optional)
Create a `.env` file for configuration:
```
PORT=8080
DB_PATH=pokemon.db
```

### Database Management
The SQLite database (`pokemon.db`) is automatically created and managed by the application.

## 🛠️ Troubleshooting

### Port Already in Use
If port 8080 is occupied, modify the port in `app.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8081)  # Change port
```

### CORS Issues
If deploying frontend and backend separately, ensure CORS is properly configured.

### Database Issues
Delete `pokemon.db` to reset the cache if needed.