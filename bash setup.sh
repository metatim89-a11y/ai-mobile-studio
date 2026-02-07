#!/bin/bash

# 1. Update system packages
echo "Updating system..."
sudo apt update

# 2. Install Python pip and venv if not present
echo "Installing Python dependencies..."
sudo apt install -y python3-pip python3-venv

# 3. Install the required Python libraries
echo "Installing project libraries..."
pip install streamlit pandas playwright

# 4. Install Playwright browser binaries
echo "Installing Playwright browsers (Chromium)..."
playwright install chromium

# 5. Install system dependencies for the browsers
echo "Installing browser system dependencies..."
playwright install-deps

echo "------------------------------------------------"
echo "✅ Setup Complete!"
echo "To start your app, run: streamlit run logistics_box.py"
echo "------------------------------------------------"