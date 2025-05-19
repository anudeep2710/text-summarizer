"""
TalkToYourDocument: Serverless API endpoint for Vercel
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import sys

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
                "groq_api_key_set": "GROQ_API_KEY" in os.environ
            }
        }
        
        self.wfile.write(json.dumps(response).encode())
        return
