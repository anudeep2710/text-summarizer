---
title: TalkToYourDocument
emoji: 📉
colorFrom: gray
colorTo: indigo
sdk: gradio
sdk_version: 5.23.3
app_file: app.py
pinned: false
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

# TalkToYourDocument

An AI-powered document question answering system that allows you to upload PDF documents and have conversations with them.

## Features

- Upload and process PDF documents
- Get document summaries automatically 
- Generate sample questions from documents
- Ask custom questions about document content
- Powerful LLM-based responses using Groq API

## API Endpoints

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/` | Root endpoint to check if API is running | None |
| GET | `/documents` | Retrieves list of all uploaded documents | None |
| POST | `/upload` | Uploads and processes a new document | `file`: PDF document (form data) |
| POST | `/query` | Queries documents with a question | JSON body: `query` (string), `document_ids` (array) |
| POST | `/summary` | Generates a summary of a document | JSON body: `document_id` (string) |
| POST | `/sample_questions` | Generates sample questions for a document | JSON body: `document_id` (string) |

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
   pip install -r requirements.txt
   ```

3. Set up your Groq API key:
   - Create a `.env` file in the root directory
   - Add the following: `GROQ_API_KEY=your_groq_api_key_here`

### Running the Application

#### Web UI

Run the application with the Gradio web interface:
```bash
python app_dotenv.py
```

#### API Server

Run just the API server for usage with mobile apps:
```bash
python app_api.py
```

## Deployment on Render

This application is configured for deployment on Render:

1. Push the code to your GitHub repository
2. Create a new Web Service on Render pointing to the repository
3. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app_api.py`
4. Add the environment variable:
   - Key: `GROQ_API_KEY`
   - Value: Your Groq API key

## Mobile App Integration

This API is designed to be consumed by Flutter mobile applications. See `app_api.py` for all available endpoints for mobile integration.

## License

MIT
