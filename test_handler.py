"""
Test the handler function directly
"""
import sys
import json
from io import BytesIO
from unittest.mock import MagicMock

# Create a mock request and response
class MockRequest:
    def __init__(self):
        self.path = "/"
        self.headers = {}
        self.client_address = ('127.0.0.1', 12345)
        self.server = MagicMock()
        self.wfile = BytesIO()
        self.rfile = BytesIO()
    
    def send_response(self, code):
        print(f"Response code: {code}")
    
    def send_header(self, name, value):
        print(f"Header: {name}: {value}")
    
    def end_headers(self):
        print("Headers ended")

# Import the handler from api/index.py
try:
    from api.index import handler
    
    # Create a mock request
    mock_request = MockRequest()
    
    # Create a handler instance
    handler_instance = handler(mock_request, mock_request.client_address, mock_request.server)
    
    # Call the do_GET method
    handler_instance.do_GET()
    
    # Get the response
    mock_request.wfile.seek(0)
    response_data = mock_request.wfile.read().decode('utf-8')
    
    # Parse the JSON response
    try:
        response_json = json.loads(response_data)
        print("\nResponse JSON:")
        print(json.dumps(response_json, indent=2))
        print("\nTest successful! The handler is working correctly.")
    except json.JSONDecodeError:
        print(f"\nError: Response is not valid JSON: {response_data}")
        
except Exception as e:
    print(f"Error testing handler: {str(e)}")
    import traceback
    traceback.print_exc()
