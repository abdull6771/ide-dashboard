#!/bin/bash

echo "🚀 IDE Dashboard Deployment Helper"
echo "===================================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Railway CLI not found. Installing..."
    npm i -g @railway/cli
fi

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Vercel CLI not found. Installing..."
    npm i -g vercel
fi

echo ""
echo "✅ Prerequisites installed!"
echo ""
echo "📋 Deployment Steps:"
echo ""
echo "STEP 1: Deploy API to Railway"
echo "------------------------------"
echo "1. Go to https://railway.app/"
echo "2. Click 'New Project' → 'Deploy from GitHub'"
echo "3. Select repository: abdull6771/ide-dashboard"
echo "4. Add environment variables:"
echo "   MYSQL_HOST=centerbeam.proxy.rlwy.net"
echo "   MYSQL_PORT=22865"
echo "   MYSQL_USER=root"
echo "   MYSQL_PASSWORD=muNxavWmbDYZgFlrFmSwbaXZANXMmIoJ"
echo "   MYSQL_DATABASE=railway"
echo ""
echo "5. Copy your Railway URL (e.g., https://xxx.railway.app)"
echo ""
read -p "Enter your Railway API URL (or press Enter to skip): " RAILWAY_URL

if [ ! -z "$RAILWAY_URL" ]; then
    echo ""
    echo "📝 Updating index.html with API URL..."
    
    # Update API URL in index.html
    sed -i.bak "s|'https://YOUR_RAILWAY_API_URL/api'|'$RAILWAY_URL/api'|g" index.html
    
    echo "✅ API URL updated!"
    echo ""
    echo "Committing changes..."
    git add index.html
    git commit -m "Update API URL to Railway deployment"
    git push origin main
    echo ""
fi

echo "STEP 2: Deploy Frontend to Vercel"
echo "----------------------------------"
echo ""
read -p "Ready to deploy to Vercel? (y/n): " DEPLOY_VERCEL

if [ "$DEPLOY_VERCEL" = "y" ]; then
    echo ""
    echo "🚀 Deploying to Vercel..."
    vercel --prod
    echo ""
    echo "✅ Deployment complete!"
    echo ""
    echo "📝 Next Steps:"
    echo "1. Test your API: $RAILWAY_URL/api/health"
    echo "2. Open your dashboard (Vercel will show URL)"
    echo "3. Check browser console for any errors"
    echo ""
else
    echo ""
    echo "To deploy manually later, run:"
    echo "  vercel --prod"
    echo ""
fi

echo "🎉 Deployment helper complete!"
echo ""
echo "📚 For detailed instructions, see DEPLOY_GUIDE.md"
