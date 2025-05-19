"""
TalkToYourDocument: Cloud-optimized API version
This version is optimized for deployment on free tiers of Render or Vercel
"""

import os
import sys
import logging
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler(sys.stdout)])

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if api_key:
    os.environ["GROQ_API_KEY"] = api_key
    print(f"GROQ API key loaded: {api_key[:5]}...")
else:
    print("WARNING: GROQ_API_KEY not found in .env file")
    # If deploying to Render, the API key should be set as an environment variable there

# Import cloud-optimized components
from retriever.llm_manager import LLMManager
from retriever.document_manager_cloud import DocumentManager
from retriever.chat_manager import ChatManager
from fastapi.responses import JSONResponse

# Create app config
class AppConfig:
    def __init__(self):
        self.gen_llm = LLMManager()
        self.doc_manager = DocumentManager()
        self.chat_manager = ChatManager(documentManager=self.doc_manager, llmManager=self.gen_llm)
        logging.info("Cloud-optimized AppConfig initialized")

app_config = AppConfig()

# Create FastAPI app
app = FastAPI(title="TalkToYourDocument API",
              description="Cloud-optimized API for document QA using LLMs",
              version="1.0.0")

# Enable CORS for client apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Pydantic models for API
class QueryRequest(BaseModel):
    query: str
    document_ids: List[str]

class SummaryRequest(BaseModel):
    document_id: str

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

@app.get("/")
async def root():
    return {"message": "TalkToYourDocument API is running (cloud-optimized version)"}

@app.get("/documents")
async def get_documents():
    """Get list of available documents"""
    try:
        documents = app_config.doc_manager.get_uploaded_documents()
        return JSONResponse(content={
            "success": True,
            "message": "Documents retrieved successfully",
            "data": {"documents": documents}
        })
    except Exception as e:
        logging.error(f"Error retrieving documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        # Read file content directly into memory
        file_content = await file.read()

        # Process the document with cloud-optimized manager
        status, filename, doc_id = app_config.doc_manager.process_document(file_content, file.filename)

        # Return response
        return JSONResponse(content={
            "success": True,
            "message": status,
            "data": {
                "filename": filename,
                "document_id": doc_id
            }
        })
    except Exception as e:
        logging.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

@app.post("/query")
async def query_document(request: QueryRequest):
    """Query documents with a question"""
    try:
        if not request.query:
            raise HTTPException(status_code=400, detail="Query is required")

        if not request.document_ids:
            raise HTTPException(status_code=400, detail="At least one document ID is required")

        # Generate chat response
        chat_history = []
        updated_history = app_config.chat_manager.generate_chat_response(
            request.query,
            request.document_ids,
            chat_history
        )

        # Extract the bot's response
        if len(updated_history) >= 2:
            response = updated_history[-1]["content"]
        else:
            response = "No response generated"

        return JSONResponse(content={
            "success": True,
            "message": "Query processed successfully",
            "data": {
                "response": response,
                "chat_history": updated_history
            }
        })
    except Exception as e:
        logging.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/summary")
async def get_summary(request: SummaryRequest):
    """Get a summary of a document"""
    try:
        if not request.document_id:
            raise HTTPException(status_code=400, detail="Document ID is required")

        # Get document chunks
        chunks = app_config.doc_manager.get_chunks(request.document_id)

        if not chunks:
            raise HTTPException(status_code=404, detail="Document not found or no chunks available")

        # Generate summary
        summary = app_config.chat_manager.generate_summary(chunks)

        return JSONResponse(content={
            "success": True,
            "message": "Summary generated successfully",
            "data": {
                "summary": summary
            }
        })
    except Exception as e:
        logging.error(f"Error generating summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Use PORT environment variable for Render compatibility
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("app_api_cloud:app", host="0.0.0.0", port=port)
