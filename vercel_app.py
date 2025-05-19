"""
TalkToYourDocument: Vercel-specific entry point
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Print environment for debugging
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Directory contents: {os.listdir('.')}")

    # Check if GROQ_API_KEY is set
    if "GROQ_API_KEY" in os.environ:
        logger.info("GROQ_API_KEY is set")
    else:
        logger.warning("GROQ_API_KEY is not set!")

    # Import the FastAPI app instance
    from app_backend_only import app
    logger.info("Successfully imported app from app_backend_only")

except Exception as e:
    logger.error(f"Error during initialization: {str(e)}")
    # Create a minimal app for debugging
    from fastapi import FastAPI
    app = FastAPI()

    @app.get("/")
    async def debug_info():
        return {
            "status": "error",
            "message": f"Application failed to initialize: {str(e)}",
            "python_version": sys.version,
            "environment_vars": [k for k in os.environ.keys()],
            "directory_contents": os.listdir('.')
        }
