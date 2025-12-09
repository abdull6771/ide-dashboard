# 🚀 Streamlit Cloud Deployment Guide

## Prerequisites

- GitHub account
- Streamlit Cloud account (sign up at https://share.streamlit.io/)
- Railway database already set up ✅

## Step 1: Push to GitHub

```bash
cd /Users/mac/Documents/PUBLIC/IDE

# Initialize git (if not already done)
git init

# Add files to git
git add dashboard.py nl_query_helper.py requirements.txt schema.sql README.md .gitignore

# Commit
git commit -m "Initial commit: Digital Economy Dashboard"

# Create repository on GitHub and link it
git remote add origin https://github.com/YOUR_USERNAME/ide-dashboard.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "New app"
3. Connect your GitHub account
4. Select your repository: `YOUR_USERNAME/ide-dashboard`
5. Main file path: `dashboard.py`
6. Click "Advanced settings"

## Step 3: Add Secrets (IMPORTANT!)

In the "Secrets" section, paste your credentials in this format:

```toml
MYSQL_HOST = "your-railway-host.rlwy.net"
MYSQL_PORT = "your-port"
MYSQL_USER = "your-username"
MYSQL_PASSWORD = "your-password"
MYSQL_DATABASE = "your-database"
GOOGLE_API_KEY = "your-google-api-key"
```

**⚠️ NEVER commit these values to Git! They should only be added in Streamlit Cloud's secrets manager.**

## Step 4: Deploy

Click "Deploy" button!

Your dashboard will be live at: `https://YOUR_APP_NAME.streamlit.app`

---

## 📋 Files That Will Be Deployed

✅ `dashboard.py` - Main application
✅ `nl_query_helper.py` - Query helper
✅ `requirements.txt` - Dependencies
✅ `README.md` - Documentation

❌ `.env` - Not deployed (secrets used instead)
❌ PDF files - Not deployed (too large)
❌ Local database - Not deployed (Railway used instead)

---

## 🔧 Troubleshooting

### If deployment fails:

1. **Check logs** in Streamlit Cloud dashboard
2. **Verify secrets** are correctly pasted (no extra quotes)
3. **Check Railway** database is running
4. **Ensure requirements.txt** has all dependencies

### Railway Database Status:

- ✅ Connected: 1,345 companies, 11,231 initiatives
- Host: centerbeam.proxy.rlwy.net:22865
- Database: railway

---

## 🎯 After Deployment

Your dashboard will be publicly accessible at your Streamlit URL!

To update: Just push to GitHub, Streamlit will auto-redeploy.

```bash
git add .
git commit -m "Update dashboard"
git push
```
