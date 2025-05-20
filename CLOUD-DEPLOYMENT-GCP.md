# Google Cloud Platform Deployment Guide

This guide explains how to deploy the TalkToYourDocument API to Google Cloud Platform (GCP) using Cloud Run.

## Prerequisites

1. [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed
2. [Docker](https://docs.docker.com/get-docker/) installed
3. A Google Cloud Platform account
4. A Groq API key

## Setup Google Cloud Project

1. Create a new Google Cloud project or select an existing one:
   ```bash
   gcloud projects create [PROJECT_ID] --name="TalkToYourDocument"
   # or
   gcloud config set project [EXISTING_PROJECT_ID]
   ```

2. Enable required APIs:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   ```

## Build and Deploy to Cloud Run

### Option 1: Build and Deploy Locally

1. Build the Docker image locally:
   ```bash
   docker build -t gcr.io/[PROJECT_ID]/text-summarizer .
   ```

2. Push the image to Google Container Registry:
   ```bash
   docker push gcr.io/[PROJECT_ID]/text-summarizer
   ```

3. Deploy to Cloud Run:
   ```bash
   gcloud run deploy text-summarizer \
     --image gcr.io/[PROJECT_ID]/text-summarizer \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars="GROQ_API_KEY=your_groq_api_key"
   ```

### Option 2: Build and Deploy with Cloud Build (Recommended)

1. Deploy directly using Cloud Build (builds and deploys in one step):
   ```bash
   gcloud builds submit --tag gcr.io/[PROJECT_ID]/text-summarizer
   
   gcloud run deploy text-summarizer \
     --image gcr.io/[PROJECT_ID]/text-summarizer \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars="GROQ_API_KEY=your_groq_api_key"
   ```

## Setting Environment Variables

You can set environment variables during deployment or update them later:

```bash
gcloud run services update text-summarizer \
  --set-env-vars="GROQ_API_KEY=your_groq_api_key"
```

## Continuous Deployment with Cloud Build

You can set up continuous deployment from GitHub:

1. Connect your GitHub repository to Cloud Build
2. Create a cloudbuild.yaml file in your repository:

```yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/text-summarizer', '.']
  
  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/text-summarizer']
  
  # Deploy container image to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'text-summarizer'
      - '--image'
      - 'gcr.io/$PROJECT_ID/text-summarizer'
      - '--platform'
      - 'managed'
      - '--region'
      - 'us-central1'
      - '--allow-unauthenticated'

images:
  - 'gcr.io/$PROJECT_ID/text-summarizer'
```

3. Set up a trigger in Cloud Build to automatically build and deploy when you push to your repository

## Monitoring and Logs

- View logs in the Cloud Run console or using gcloud:
  ```bash
  gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=text-summarizer" --limit 50
  ```

- Monitor performance in the Cloud Run dashboard

## Cost Management

Cloud Run charges based on:
1. Number of requests
2. Time your container instances spend processing requests
3. Memory allocated to your container instances

The free tier includes:
- 2 million requests per month
- 360,000 GB-seconds of memory
- 180,000 vCPU-seconds of compute time

To minimize costs:
- Set appropriate memory limits (default is 256MB)
- Configure concurrency settings
- Set minimum instances to 0 to scale to zero when not in use

## Troubleshooting

If you encounter issues:

1. Check container logs in Cloud Run console
2. Verify environment variables are set correctly
3. Test the container locally before deploying:
   ```bash
   docker build -t text-summarizer .
   docker run -p 8080:8080 -e GROQ_API_KEY=your_key text-summarizer
   ```
4. Check that your container is listening on the port specified by the PORT environment variable

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Container Registry Documentation](https://cloud.google.com/container-registry/docs)
