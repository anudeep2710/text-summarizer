"""
Simple HTTP server for testing
"""
import http.server
import socketserver
import json
import sys

class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "message": "API is running (simple server)",
            "status": "ok",
            "path": self.path,
            "python_version": sys.version
        }
        
        self.wfile.write(json.dumps(response).encode())

def run_server(port=9000):
    with socketserver.TCPServer(("", port), SimpleHandler) as httpd:
        print(f"Server running at http://localhost:{port}")
        httpd.serve_forever()

if __name__ == "__main__":
    PORT = 9000
    print(f"Starting server on port {PORT}...")
    print(f"Python version: {sys.version}")
    
    try:
        run_server(PORT)
    except OSError as e:
        if "Only one usage of each socket address" in str(e):
            # Try a different port
            PORT = 9001
            print(f"Port {PORT-1} is in use. Trying port {PORT}...")
            run_server(PORT)
        else:
            raise
