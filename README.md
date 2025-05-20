# TalkToYourDocument (Backend-Only)

A backend-only API for document question answering, optimized for deployment on Google Cloud Platform.

## Features

- Upload and process PDF documents
- Get document summaries automatically
- Ask custom questions about document content
- Powerful LLM-based responses using Groq API
- Backend-only for minimal storage usage
- No frontend dependencies
- **Multilingual support** for documents, queries, and responses
  - Automatic language detection
  - Cross-language document search
  - Translation between languages

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
  "document_ids": ["document1.pdf"],
  "query_language": "en",
  "target_language": "es"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Query processed successfully",
  "data": {
    "response": "El tema principal de este documento es...",
    "chat_history": [
      {"role": "user", "content": "What is the main topic of this document?"},
      {"role": "assistant", "content": "El tema principal de este documento es...\n\n[Response translated from en to es]"}
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

## Multilingual Support

This API supports multilingual document processing, queries, and responses:

### Supported Languages

- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Dutch (nl)
- Russian (ru)
- Chinese (Simplified) (zh-cn)
- Chinese (Traditional) (zh-tw)
- Japanese (ja)
- Korean (ko)
- Arabic (ar)
- Hindi (hi)
- Bengali (bn)
- Urdu (ur)
- Telugu (te)
- Tamil (ta)
- Marathi (mr)
- Gujarati (gu)

### Language Parameters

When making API requests, you can specify:

- `query_language`: The language of your query (auto-detected if not specified)
- `target_language`: The language you want the response in

Example:
```json
{
  "query": "¿Cuál es el tema principal?",
  "document_ids": ["document1.pdf"],
  "query_language": "es",
  "target_language": "en"
}
```

This will:
1. Process the Spanish query
2. Search for relevant content in the document
3. Return the response in English

### Cross-Language Search

The system can search documents in one language using queries in another language, making your document collection accessible regardless of language barriers.

## Mobile App Integration

This API is designed to be consumed by Flutter mobile applications. See `app_api.py` for all available endpoints for mobile integration.

## License

MIT
