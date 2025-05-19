"""
TalkToYourDocument: FastAPI version for Vercel
"""
import os
import sys
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Create a FastAPI app
app = FastAPI(title="TalkToYourDocument API",
              description="Minimal API for document QA using LLMs",
              version="1.0.0")

@app.get("/")
async def root(request: Request):
    return JSONResponse({
        "message": "TalkToYourDocument API is running (FastAPI version)",
        "status": "ok",
        "path": str(request.url),
        "environment": {
            "python_version": sys.version,
            "groq_api_key_set": "GROQ_API_KEY" in os.environ,
            "directory_contents": os.listdir('.')
        }
    })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}
