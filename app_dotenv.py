"""
TalkToYourDocument: A document QA application using Gradio and LangChain
This version loads environment variables from .env file directly
"""

import os
import sys
import logging
from dotenv import load_dotenv
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler(sys.stdout)])

# Define the path to the .env file
env_path = Path('.') / '.env'

# Load environment variables with explicit path
try:
    print(f"Attempting to load .env file from: {env_path.absolute()}")
    # Check if file exists
    if not env_path.exists():
        print(f"WARNING: .env file not found at {env_path.absolute()}")
    else:
        # Check file size and readability
        try:
            with open(env_path, 'r') as f:
                content = f.read()
                print(f"Successfully read .env file, content length: {len(content)} characters")
        except Exception as e:
            print(f"ERROR reading .env file: {str(e)}")
    
    # Try loading with dotenv
    load_dotenv(dotenv_path=env_path)
except Exception as e:
    print(f"ERROR loading .env file: {str(e)}")

# Get the API key with fallback
api_key = os.getenv("GROQ_API_KEY")
if api_key:
    os.environ["GROQ_API_KEY"] = api_key
    print(f"GROQ API key loaded: {api_key[:5]}...")
else:
    print("WARNING: GROQ_API_KEY not found in .env file")
    
    # Last resort: hardcode the key (only as a fallback)
    os.environ["GROQ_API_KEY"] = "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"
    print("Using hardcoded API key as fallback")

# Now import the app
from app import *

# The rest of the app is imported from app.py
if __name__ == "__main__":
    print("Application started with .env support") 