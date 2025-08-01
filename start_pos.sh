#!/bin/bash

echo "Point of Sale System - Starting..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    echo "Please install Python 3.8 or newer"
    exit 1
fi

# Change to script directory
cd "$(dirname "$0")"

# Run the POS system
echo "Starting POS system..."
if command -v python3 &> /dev/null; then
    python3 main.py
else
    python main.py
fi

if [ $? -ne 0 ]; then
    echo
    echo "An error occurred while starting the application"
    read -p "Press Enter to continue..."
fi
