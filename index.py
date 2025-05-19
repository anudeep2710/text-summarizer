"""
TalkToYourDocument: Alternative entry point for Vercel
"""
import os
import sys

# Import the app from vercel_app.py
try:
    from vercel_app import app
    print("Successfully imported app from vercel_app")
except Exception as e:
    print(f"Error importing app from vercel_app: {str(e)}")
    # Create a minimal WSGI app as fallback
    def app(environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return [b"Error: Could not import app from vercel_app.py"]
