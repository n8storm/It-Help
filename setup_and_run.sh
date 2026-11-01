#!/bin/bash
echo "Setting up IT Help Desk App..."
cd /Users/n8storm/it_helpdesk

# Install dependencies using pip3 (Standard for macOS)
pip3 install -r requirements.txt

echo "Starting server on http://127.0.0.1:8080 ..."
echo "Press Ctrl+C to stop the server."
python3 app.py
