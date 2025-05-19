---
title: TalkToYourDocument (Backend-Only)
emoji: 📉
colorFrom: gray
colorTo: indigo
sdk: fastapi
sdk_version: 0.115.0
app_file: app_backend_only.py
pinned: false
---

# TalkToYourDocument (Backend-Only)

A backend-only API for document question answering, optimized for deployment on free tiers of Render or Vercel.

## Features

- Upload and process PDF documents
- Get document summaries automatically
- Ask custom questions about document content
- Powerful LLM-based responses using Groq API
- Backend-only for minimal storage usage
- No frontend dependencies

## API Endpoints

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/` | Root endpoint to check if API is running | None |
| GET | `/documents` | Retrieves list of all uploaded documents | None |
| POST | `/upload` | Uploads and processes a new document | `file`: PDF document (form data) |
| POST | `/query` | Queries documents with a question | JSON body: `query` (string), `document_ids` (array) |
| POST | `/summary` | Generates a summary of a document | JSON body: `document_id` (string) |

## Request & Response Examples

### GET /documents
**Response:**
```json
{
  "success": true,
  "message": "Documents retrieved successfully",
  "data": {
    "documents": ["document1.pdf", "document2.pdf"]
  }
}
```

### POST /upload
**Request:** Form data with file upload

**Response:**
```json
{
  "success": true,
  "message": "Document processed successfully",
  "data": {
    "filename": "document.pdf",
    "document_id": "doc_123"
  }
}
```

### POST /query
**Request:**
```json
{
  "query": "What is the main topic of this document?",
  "document_ids": ["document1.pdf"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Query processed successfully",
  "data": {
    "response": "The main topic of this document is...",
    "chat_history": [
      {"role": "user", "content": "What is the main topic of this document?"},
      {"role": "assistant", "content": "The main topic of this document is..."}
    ]
  }
}
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Groq API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/anudeep2710/text-summarizer.git
   cd text-summarizer
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements-slim.txt
   ```

3. Set up your Groq API key:
   - Create a `.env` file in the root directory
   - Add the following: `GROQ_API_KEY=your_groq_api_key_here`

### Running the Application

Run the backend-only API server:
```bash
python app_backend_only.py
```

## Deployment on Render

This backend-only application is optimized for deployment on Render's free tier:

1. Push the code to your GitHub repository
2. Create a new Web Service on Render pointing to the repository
3. Use the following settings:
   - Build Command: `pip install -r requirements-slim.txt`
   - Start Command: `python app_backend_only.py`
4. Add the environment variable:
   - Key: `GROQ_API_KEY`
   - Value: Your Groq API key

## Deployment on Vercel

This backend-only application can also be deployed on Vercel's free tier:

1. Push the code to your GitHub repository
2. Connect your repository to Vercel
3. Set the following configuration:
   - Framework Preset: Other
   - Build Command: `pip install -r requirements-slim.txt`
   - Output Directory: `.`
   - Install Command: `pip install -r requirements-slim.txt`
4. Add the environment variable:
   - Key: `GROQ_API_KEY`
   - Value: Your Groq API key

For more detailed deployment instructions, see [CLOUD-DEPLOYMENT.md](CLOUD-DEPLOYMENT.md)

## Connecting to the Backend

Since this is a backend-only application, you'll need to create your own frontend or use API tools like Postman to interact with it. The API endpoints are documented above.

## Mobile App Integration

This API is designed to be consumed by Flutter mobile applications. See `app_api.py` for all available endpoints for mobile integration.

## License

MIT
