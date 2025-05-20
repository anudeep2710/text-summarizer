"""
Test the Vercel deployment
"""
import requests
import json
import sys

def test_vercel_deployment(url):
    """Test a Vercel deployment by making a GET request to the URL"""
    print(f"Testing Vercel deployment at: {url}")
    
    try:
        response = requests.get(url)
        
        print(f"Status code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print("\nResponse JSON:")
            print(json.dumps(response_json, indent=2))
        except json.JSONDecodeError:
            print(f"\nResponse is not JSON: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("\nTest successful! The deployment is working correctly.")
        else:
            print(f"\nWarning: Received status code {response.status_code}")
            
    except requests.RequestException as e:
        print(f"Error making request: {str(e)}")

if __name__ == "__main__":
    # Default URL to test
    default_url = "https://text-summarizer-anudeeps-projects-6195916f.vercel.app/"
    
    # Get URL from command line if provided
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = default_url
    
    test_vercel_deployment(url)
