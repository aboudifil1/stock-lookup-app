# 🚀 Quick Start Guide

## ✅ What's Already Done

1. ✅ **ngrok is installed** at `~/bin/ngrok`
2. ✅ **Streamlit app is ready** with improved layout
3. ✅ **API key is configured**

## 🌐 Getting a Public URL (Choose One)

### Option 1: ngrok (Quick, but requires free signup)

**One-time setup (2 minutes):**
1. Sign up for free: https://dashboard.ngrok.com/signup
2. Get your authtoken: https://dashboard.ngrok.com/get-started/your-authtoken
3. Run:
   ```bash
   ~/bin/ngrok config add-authtoken YOUR_TOKEN_HERE
   ```

**Then start the tunnel:**
```bash
./setup_ngrok.sh
```

Or manually:
```bash
~/bin/ngrok http 8501
```

Copy the `Forwarding` URL and share it!

### Option 2: Streamlit Cloud (Permanent, Recommended)

1. Push your code to GitHub
2. Go to https://share.streamlit.io
3. Sign in with GitHub
4. Click "New app"
5. Select your repository
6. Main file: `app.py`
7. Click "Deploy"
8. Get a permanent URL like: `https://your-app-name.streamlit.app`

**This is FREE and the URL never changes!**

## 🎨 View Your App

- **Local:** http://localhost:8501
- **Network (same WiFi):** http://192.168.1.209:8501
- **Public:** Use ngrok or Streamlit Cloud (see above)

## 📝 Notes

- ngrok free accounts: 2-hour sessions, URL changes on restart
- Streamlit Cloud: Permanent URL, always available
