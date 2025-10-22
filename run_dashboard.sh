#!/bin/bash

# QuickBite Express Dashboard Launcher
# This script starts the Streamlit dashboard

echo "🍔 Starting QuickBite Express Crisis Analysis Dashboard..."
echo ""
echo "📊 Dashboard Features:"
echo "  • Executive Summary"
echo "  • Business Health Analysis"
echo "  • Customer Analytics"
echo "  • Operational Performance"
echo "  • Restaurant Insights"
echo "  • Recovery Roadmap"
echo ""
echo "🌐 Dashboard will open at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""

# Activate virtual environment and run streamlit
source .venv/bin/activate
streamlit run dashboard.py
