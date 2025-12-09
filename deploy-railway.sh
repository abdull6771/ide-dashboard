#!/bin/bash
# Quick Deployment Script for Dash Dashboard to Railway

echo "🚀 Deploying Dash Dashboard to Railway..."
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm i -g @railway/cli
fi

# Login to Railway
echo "📝 Step 1: Login to Railway"
railway login

# Link to project (or create new)
echo ""
echo "🔗 Step 2: Link to Railway project"
echo "If you have an existing project, select it. Otherwise, create a new one."
railway link

# Add environment variables
echo ""
echo "⚙️  Step 3: Setting environment variables"
echo "Adding database credentials..."

railway variables --set "MYSQL_HOST=centerbeam.proxy.rlwy.net" \
                  --set "MYSQL_PORT=22865" \
                  --set "MYSQL_USER=root" \
                  --set "MYSQL_PASSWORD=muNxavWmbDYZgFlrFmSwbaXZANXMmIoJ" \
                  --set "MYSQL_DATABASE=railway" \
                  --set "PORT=8050" \
                  --skip-deploys

echo ""
echo "✅ Environment variables added!"

# Deploy
echo ""
echo "🚀 Step 4: Deploy application"
railway up

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Wait 2-3 minutes for deployment to finish"
echo "2. Run: railway open"
echo "3. Your dashboard will open in the browser"
echo ""
echo "📊 To view logs: railway logs"
echo "🔍 To check status: railway status"
