"""
Minimal Vercel Serverless Function
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
            "message": "API is running",
            "status": "ok",
            "python_version": sys.version
        }

        self.wfile.write(json.dumps(response).encode())
        return
