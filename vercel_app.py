"""
TalkToYourDocument: Vercel-specific entry point
"""
import os
import sys
import json

# Simple logging to stdout since we can't rely on logging module
def log(message):
    print(message, flush=True)

log(f"Python version: {sys.version}")
log(f"Current directory: {os.getcwd()}")
log(f"Directory contents: {os.listdir('.')}")

# Check if requirements.txt exists
if os.path.exists("requirements.txt"):
    log("requirements.txt exists")
    with open("requirements.txt", "r") as f:
        log(f"requirements.txt content: {f.read()}")
else:
    log("WARNING: requirements.txt not found!")

# Check if GROQ_API_KEY is set
if "GROQ_API_KEY" in os.environ:
    log("GROQ_API_KEY is set")
else:
    log("WARNING: GROQ_API_KEY is not set!")

# Try to import FastAPI first to check if dependencies are installed
try:
    from fastapi import FastAPI
    log("FastAPI imported successfully")

    # Now try to import the app
    try:
        from app_backend_only import app
        log("Successfully imported app from app_backend_only")
    except Exception as e:
        log(f"Error importing app_backend_only: {str(e)}")
        # Create a minimal app for debugging
        app = FastAPI()

        @app.get("/")
        async def debug_info():
            return {
                "status": "error",
                "message": f"Error importing app_backend_only: {str(e)}",
                "python_version": sys.version,
                "environment_vars": list(os.environ.keys()),
                "directory_contents": os.listdir('.')
            }

except ImportError:
    # FastAPI not installed, create a minimal WSGI app
    log("ERROR: FastAPI not installed!")

    def app(environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type', 'application/json')]
        start_response(status, response_headers)

        response_body = json.dumps({
            "status": "error",
            "message": "FastAPI not installed. Check Vercel build logs.",
            "python_version": sys.version,
            "environment_vars": list(os.environ.keys()),
            "directory_contents": os.listdir('.')
        })

        return [response_body.encode()]
