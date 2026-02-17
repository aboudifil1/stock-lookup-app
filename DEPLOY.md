# 🚀 Deploy to Streamlit Cloud - Step by Step

## ✅ What's Ready

- ✅ Git repository initialized
- ✅ All files prepared for deployment
- ✅ `.gitignore` configured to exclude secrets

## 📋 Deployment Steps

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `stock-lookup-app` (or any name you like)
3. Make it **Public** (required for free Streamlit Cloud)
4. **Don't** initialize with README, .gitignore, or license
5. Click "Create repository"

### Step 2: Push Your Code to GitHub

Run these commands in your terminal:

```bash
cd "/Users/aboudifil/projects/Cursor APP 1"

# Add all files
git add .

# Commit
git commit -m "Initial commit: Stock Lookup Streamlit app"

# Add your GitHub repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/stock-lookup-app.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io
2. Sign in with your **GitHub account**
3. Click **"New app"**
4. Fill in:
   - **Repository:** Select your repository (e.g., `YOUR_USERNAME/stock-lookup-app`)
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** (optional) Choose a custom subdomain
5. Click **"Advanced settings"** → **"Secrets"**
6. Add your API key:
   ```
   FINNHUB_API_KEY = "your_actual_api_key_here"
   ```
7. Click **"Deploy"**

### Step 4: Share Your App! 🎉

Once deployed, you'll get a URL like:
```
https://your-app-name.streamlit.app
```

**This URL is permanent and can be shared with anyone!**

## 🔒 Security Notes

- ✅ Your `.env.local` file is already in `.gitignore` (won't be committed)
- ✅ `.streamlit/secrets.toml` is in `.gitignore` (won't be committed)
- ✅ API key should be added in Streamlit Cloud's Secrets section (not in code)

## 🐛 Troubleshooting

**If deployment fails:**
- Check that `requirements.txt` includes all dependencies
- Verify `app.py` is in the root directory
- Make sure the API key is set in Streamlit Cloud Secrets

**If the app loads but shows API key error:**
- Go to your app settings on Streamlit Cloud
- Click "Secrets" and verify `FINNHUB_API_KEY` is set correctly

## 📝 Next Steps After Deployment

- Your app will auto-update when you push changes to GitHub
- You can view logs in the Streamlit Cloud dashboard
- Share the URL with friends - no setup needed on their end!
