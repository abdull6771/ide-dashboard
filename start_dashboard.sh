#!/bin/bash

# Start the Flask API server
echo "🚀 Starting Flask API server on http://localhost:5000"
echo "📊 Dashboard will be available at http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Install dependencies if not already installed
pip3 install Flask Flask-CORS pymysql python-dotenv 2>/dev/null

# Start Flask API in background
python3 api.py &
API_PID=$!

# Wait a moment for API to start
sleep 2

# Start simple HTTP server for the HTML
python3 -m http.server 8000 &
HTTP_PID=$!

# Open browser
open http://localhost:8000/index.html

echo ""
echo "✅ Servers started!"
echo "   API: http://localhost:5000"
echo "   Dashboard: http://localhost:8000/index.html"
echo ""
echo "To stop servers, press Ctrl+C"

# Wait for Ctrl+C
trap "kill $API_PID $HTTP_PID; exit" INT
wait
