"""
TalkToYourDocument: Vercel-specific entry point
"""

# Import the FastAPI app instance
from app_backend_only import app

# This file is necessary for Vercel deployment
# Vercel looks for a variable named 'app' to serve as the entry point
