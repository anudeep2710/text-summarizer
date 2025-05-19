#!/bin/bash

echo "Starting build process..."

# List directory contents
echo "Directory contents:"
ls -la

# Install dependencies
echo "Installing dependencies from requirements-vercel.txt..."
pip install -r requirements-vercel.txt

# Print Python version for debugging
echo "Python version:"
python --version

# Print installed packages for debugging
echo "Installed packages:"
pip list

# Check if key files exist
echo "Checking for key files:"
if [ -f "vercel_app.py" ]; then
    echo "vercel_app.py exists"
else
    echo "ERROR: vercel_app.py not found!"
fi

if [ -f "app_backend_only.py" ]; then
    echo "app_backend_only.py exists"
else
    echo "ERROR: app_backend_only.py not found!"
fi

# Check for retriever directory
if [ -d "retriever" ]; then
    echo "retriever directory exists"
    ls -la retriever/
else
    echo "ERROR: retriever directory not found!"
fi

echo "Build process completed"
