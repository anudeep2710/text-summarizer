"""
Test the API locally
"""
import http.server
import socketserver
import sys
import os
from api.index import handler

class TestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Use our Vercel handler
        self.handler = handler(self, self.client_address, self.server)
        self.handler.do_GET()

def main():
    # Set up a simple HTTP server
    PORT = 8080

    print(f"Starting server on port {PORT}...")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")

    with socketserver.TCPServer(("", PORT), TestHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped by user")
            httpd.server_close()

if __name__ == "__main__":
    main()
