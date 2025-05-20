# TalkToYourDocument (Backend-Only)

A backend-only API for document question answering, optimized for deployment on Google Cloud Platform.

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

## Deployment on Google Cloud Platform

This application is optimized for deployment on Google Cloud Platform using Cloud Run:

1. Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. Build and deploy using Cloud Run:
   ```bash
   # Build and deploy in one step
   gcloud builds submit --tag gcr.io/[PROJECT_ID]/text-summarizer

   gcloud run deploy text-summarizer \
     --image gcr.io/[PROJECT_ID]/text-summarizer \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars="GROQ_API_KEY=your_groq_api_key"
   ```

For more detailed GCP deployment instructions, see [CLOUD-DEPLOYMENT-GCP.md](CLOUD-DEPLOYMENT-GCP.md)

## Connecting to the Backend

Since this is a backend-only application, you'll need to create your own frontend or use API tools like Postman to interact with it. The API endpoints are documented above.

## Mobile App Integration

This API is designed to be consumed by Flutter mobile applications. See `app_api.py` for all available endpoints for mobile integration.

## License

MIT
