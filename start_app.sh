#!/bin/bash

# Navigate to the project directory (ensure you're in the right folder)
cd ~/file_analysis_app

# Activate the virtual environment
source venv/bin/activate

# Start Tika server in the background
java -jar tika-server.jar &

# Wait for a few seconds to ensure Tika starts properly
sleep 5

# Run the Flask app
python3 app.py
