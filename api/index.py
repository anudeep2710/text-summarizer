"""
TalkToYourDocument: Serverless API endpoint for Vercel
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Simple logging to stdout
def log(message):
    print(message, flush=True)

log(f"Python version: {sys.version}")
log(f"Current directory: {os.getcwd()}")
log(f"Directory contents: {os.listdir('.')}")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response = {
            "message": "TalkToYourDocument API is running (Vercel serverless version)",
            "status": "ok",
            "path": self.path,
            "environment": {
                "python_version": sys.version,
                "groq_api_key_set": "GROQ_API_KEY" in os.environ,
                "directory_contents": os.listdir('.')
            }
        }

        self.wfile.write(json.dumps(response).encode())
        return
