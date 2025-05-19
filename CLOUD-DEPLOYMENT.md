# Cloud Deployment Guide for TalkToYourDocument (Backend-Only)

This guide explains how to deploy the backend-only version of TalkToYourDocument on free tiers of Render or Vercel.

## Optimizations for Free Tier Deployment

The backend-only version includes the following changes to reduce storage requirements:

1. **Slimmed-down dependencies**: Only essential packages are included
2. **In-memory vector storage**: No local file storage for embeddings
3. **Temporary file handling**: Files are processed in memory when possible
4. **Reduced model footprint**: Using API-based LLMs only
5. **No frontend dependencies**: Removed all frontend-related code and dependencies

## Deployment on Render

1. Push your code to GitHub
2. Log in to [Render](https://render.com)
3. Create a new Web Service
4. Connect to your GitHub repository
5. Use the following settings:
   - **Name**: TalkToYourDocument (or your preferred name)
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements-slim.txt`
   - **Start Command**: `python app_backend_only.py`
6. Add the environment variable:
   - **Key**: `GROQ_API_KEY`
   - **Value**: Your Groq API key
7. Click "Create Web Service"

Alternatively, you can use the `render-cloud.yaml` file for deployment:

```bash
render blueprint render-cloud.yaml
```

Note that this is a backend-only application, so you'll need to create your own frontend or use API tools to interact with it.

## Deployment on Vercel

1. Install the Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Log in to Vercel:
   ```bash
   vercel login
   ```

3. Deploy the application:
   ```bash
   vercel
   ```

4. Add the environment variable in the Vercel dashboard:
   - **Key**: `GROQ_API_KEY`
   - **Value**: Your Groq API key

## API Usage

The cloud-optimized API provides the same endpoints as the original version:

- `GET /`: Check if the API is running
- `GET /documents`: Get list of uploaded documents
- `POST /upload`: Upload and process a document
- `POST /query`: Query documents with a question
- `POST /summary`: Generate a summary of a document

## Storage Limitations

The free tiers of Render and Vercel have storage limitations:

- **Render**: 512 MB disk space
- **Vercel**: 1 GB disk space

The cloud-optimized version minimizes disk usage by:
1. Using in-memory storage for vector embeddings
2. Processing files in memory when possible
3. Using API-based LLMs instead of downloading models

## Additional Tips

1. **Clear unused files**: Regularly clean up temporary files
2. **Limit document size**: Avoid uploading very large documents
3. **Monitor usage**: Keep an eye on your storage usage in the dashboard
4. **Consider serverless**: For Vercel, consider using serverless functions for specific endpoints

## Troubleshooting

If you encounter storage issues:
1. Check the logs for any file-related errors
2. Verify that temporary files are being cleaned up
3. Consider further reducing dependencies if needed
4. For persistent storage needs, consider using a cloud storage service like AWS S3
