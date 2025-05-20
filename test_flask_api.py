"""
Test the API locally using Flask
"""
import json
import sys
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        "message": "API is running (Flask test)",
        "status": "ok",
        "python_version": sys.version
    })

@app.route('/api')
def api_index():
    """API endpoint"""
    return jsonify({
        "message": "API endpoint is running",
        "status": "ok",
        "python_version": sys.version
    })

if __name__ == '__main__':
    print("Starting Flask server on port 5000...")
    print(f"Python version: {sys.version}")
    app.run(debug=True)
