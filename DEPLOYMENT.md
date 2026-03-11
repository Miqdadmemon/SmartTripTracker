# Deployment Guide for Smart Trip Tracker

## Local Development
```bash
cd SmartTripTracker
pip install -r requirements.txt
python app.py
```

---

## Option 1: Deploy to Render.com (Free)

### Prerequisites
- Git installed
- GitHub account

### Steps
1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   # Create a new repository on GitHub and push
   ```

2. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

3. **Deploy**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Settings:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `python app.py`
   - Click "Create Web Service"

4. **Environment Variables**
   - In Render dashboard, add:
     - `SECRET_KEY`: Your secret key
     - `DATABASE_URL`: SQLite (for free tier, use the default)

---

## Option 2: Deploy to Railway

### Steps
1. **Push to GitHub** (same as above)

2. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

3. **Deploy**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect Flask

4. **Environment Variables**
   - Add `SECRET_KEY` in variables tab

---

## Option 3: Deploy to Heroku

### Prerequisites
- Heroku CLI installed

### Steps
1. **Create Procfile**
   ```bash
   echo "web: python app.py" > Procfile
   ```

2. **Push to GitHub** and connect to Heroku, or use Heroku CLI:
   ```bash
   heroku login
   heroku create your-app-name
   git push heroku main
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   ```

---

## Option 4: Deploy to PythonAnywhere

### Steps
1. **Create Account**
   - Go to [pythonanywhere.com](https://pythonanywhere.com)

2. **Upload Files**
   - Use the "Files" tab to upload your project

3. **Configure Web App**
   - Go to "Web" tab
   - Add new web app
   - Select "Flask" and Python version
   - Edit WSGI configuration file

4. **Install Dependencies**
   - Open Bash console
   - ```bash
     pip install -r requirements.txt
     ```

5. **Reload the app**

---

## Production Settings (config.py)

Update your `config.py` for production:

```python
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # Use PostgreSQL for production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://user:pass@localhost/smarttrip'
```

---

## Database Migration to PostgreSQL

For production, use PostgreSQL:

```bash
pip install psycopg2-binary
export DATABASE_URL="postgresql://user:pass@localhost/smarttrip"
```

---

## Recommended: Render.com Deployment Steps

### Detailed Steps:

1. **Prepare for Deployment**
   ```bash
   # Update requirements.txt
   echo "Flask==3.0.0
   Flask-SQLAlchemy==3.1.1
   Flask-Login==0.6.3
   gunicorn==21.2.0" > requirements.txt
   
   # Create Procfile
   echo "web: gunicorn app:app --workers 4" > Procfile
   ```

2. **Update app.py for Production**
   - Change port: `port = int(os.environ.get('PORT', 5000))`
   - Add: `app.run(host='0.0.0.0', port=port)`

3. **Deploy**
   - Push to GitHub
   - Connect to Render
   - Deploy!

---

## Quick Deploy to Render (Summary)

1. Push code to GitHub
2. Go to render.com → New Web Service
3. Connect GitHub repo
4. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Click Deploy

---

## Troubleshooting

- **Static files not loading**: Ensure `static` folder exists
- **Database errors**: Use PostgreSQL for production
- **Import errors**: Check Python version compatibility

---

## Support
For deployment help, check:
- [Render Docs](https://render.com/docs)
- [Flask Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)

