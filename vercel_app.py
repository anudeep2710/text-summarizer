"""
TalkToYourDocument: Standalone Vercel-compatible API
"""
import os
import sys
import json
from typing import List, Optional, Dict, Any

# Simple logging to stdout
def log(message):
    print(message, flush=True)

log(f"Python version: {sys.version}")
log(f"Current directory: {os.getcwd()}")
log(f"Directory contents: {os.listdir('.')}")

# Check if GROQ_API_KEY is set
if "GROQ_API_KEY" in os.environ:
    log("GROQ_API_KEY is set")
else:
    log("WARNING: GROQ_API_KEY is not set!")

# Create a minimal FastAPI app that doesn't depend on other modules
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from fastapi.responses import JSONResponse

    log("Successfully imported FastAPI and related modules")

    # Create a minimal FastAPI app
    app = FastAPI(title="TalkToYourDocument API",
                  description="Minimal API for document QA using LLMs",
                  version="1.0.0")

    # Enable CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Define API models
    class APIResponse(BaseModel):
        success: bool
        message: str
        data: Optional[Dict[str, Any]] = None

    @app.get("/")
    async def root():
        return {
            "message": "TalkToYourDocument API is running (Vercel minimal version)",
            "status": "ok",
            "environment": {
                "python_version": sys.version,
                "groq_api_key_set": "GROQ_API_KEY" in os.environ
            }
        }

    @app.get("/documents")
    async def get_documents():
        """Get list of available documents (placeholder)"""
        return JSONResponse(content={
            "success": True,
            "message": "This is a placeholder endpoint. The full functionality requires additional setup.",
            "data": {"documents": []}
        })

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "version": "1.0.0"}

except ImportError as e:
    log(f"ERROR: Could not import FastAPI: {str(e)}")

    # Create a minimal WSGI app as fallback
    def app(environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type', 'application/json')]
        start_response(status, response_headers)

        response_body = json.dumps({
            "status": "error",
            "message": f"Could not import FastAPI: {str(e)}",
            "python_version": sys.version,
            "environment_vars": list(os.environ.keys()),
            "directory_contents": os.listdir('.')
        })

        return [response_body.encode()]
