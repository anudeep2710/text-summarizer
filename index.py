"""
Minimal Python API for Vercel
"""
import json
import sys

def app(environ, start_response):
    """
    Simple WSGI app for Vercel
    """
    status = '200 OK'
    response_headers = [('Content-type', 'application/json')]
    start_response(status, response_headers)

    response = {
        "message": "API is running (root handler)",
        "status": "ok",
        "python_version": sys.version
    }

    return [json.dumps(response).encode()]
