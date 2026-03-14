# SOW Generator - Cloud Run Deployment Guide

This guide provides instructions for deploying the SOW Generator application to Google Cloud Run.

## Prerequisites

Before deploying, ensure you have the following:

1. **Google Cloud Project** with billing enabled
2. **Google Cloud SDK (gcloud CLI)** installed and configured
3. **Docker** installed (for local testing)
4. **Required APIs enabled**:
   - Cloud Run API
   - Cloud Build API
   - Artifact Registry API
   - Vertex AI API
   - Cloud Storage API
   - **Google Slides API** (for PPTX to PDF conversion)
   - **Google Drive API** (for file operations)

5. **Service Account** with the following permissions:
   - Cloud Run Admin
   - Cloud Build Service Account
   - Storage Admin
   - Vertex AI User
   - **Google Slides API** access
   - **Google Drive API** access

## Application Dependencies

The SOW Generator uses **Google Slides API** for PPTX to PDF conversion:

- **Google Slides API**: Native, high-quality PPTX to PDF conversion
  - No additional system dependencies required
  - Uses service account authentication
  - Temporary Google Drive files are automatically cleaned up
  - Final Docker image size: ~200-300MB (lightweight!)

**Benefits over LibreOffice approach:**
- ✅ Smaller Docker image (500-600MB reduction)
- ✅ Faster cold starts on Cloud Run
- ✅ Better conversion quality (native Google conversion)
- ✅ No Java runtime or LibreOffice packages needed
- ✅ Already integrated with your GCP ecosystem

**Important**: Ensure your service account has the following IAM roles:
- `roles/drive.file` - Create and manage temporary Drive files
- `roles/slides.readonly` - Read Slides presentations

## Artifact Storage

The SOW Generator uses **ADK's Artifact Service** for managing PDF files in a two-tool workflow:

**Two-Tool Workflow Architecture:**
1. **Tool 1 (convert_slides_to_pdf)**: Converts PPTX to PDF using Google Slides API
   - After-tool callback: Saves PDF as artifact
2. **Tool 2 (extract_sow_from_pdf)**: Extracts structured data from PDF
   - Before-tool callback: Loads PDF artifact from tool 1

**Artifact Service Features:**
- **Automatic Versioning**: Each converted PDF is automatically versioned
- **GCS Storage**: Artifacts are stored in the configured GCS bucket (via `ARTIFACT_SERVICE_URI`)
- **Session/User Scoping**: Artifacts can be scoped to specific sessions or users
- **Callback-Managed**: Artifact saving/loading handled automatically by callbacks

**Configuration**:
Set the `ARTIFACT_SERVICE_URI` environment variable to your GCS bucket:
```bash
ARTIFACT_SERVICE_URI=gs://your-artifact-bucket
```

The artifact service will automatically organize artifacts under:
```
gs://your-artifact-bucket/artifacts/{app_name}/{user_id}/{session_id}/{filename}
```

**Note**: The application uses an **in-memory artifact service** for testing and development. For production, configure a GCS-based artifact service.

## Quick Deployment

### Option 1: Using the Deployment Script (Recommended)

```bash
# Make the script executable
chmod +x deploy.sh

# Run the deployment
./deploy.sh
```

The script will:
- Check prerequisites
- Enable required APIs
- Create Artifact Registry repository (if needed)
- Build and deploy the application using Cloud Build
- Display the service URL

### Option 2: Using Cloud Build Directly

```bash
# Set your project ID
export PROJECT_ID="your-project-id"

# Submit build to Cloud Build
gcloud builds submit \
  --config=cloudbuild.yaml \
  --project="${PROJECT_ID}"
```

### Option 3: Manual Deployment

```bash
# 1. Build the Docker image
docker build -t gcr.io/${PROJECT_ID}/sow-generator:latest .

# 2. Push to Container Registry
docker push gcr.io/${PROJECT_ID}/sow-generator:latest

# 3. Deploy to Cloud Run
gcloud run deploy sow-generator \
  --image=gcr.io/${PROJECT_ID}/sow-generator:latest \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --min-instances=0 \
  --max-instances=10 \
  --timeout=300s \
  --port=8080 \
  --set-env-vars=GOOGLE_CLOUD_PROJECT=${PROJECT_ID}
```

## Configuration

### Environment Variables

The application requires the following environment variables to be set:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GOOGLE_CLOUD_PROJECT` | GCP Project ID | Yes | - |
| `GOOGLE_CLOUD_LOCATION` | Vertex AI region | No | us-central1 |
| `AGENT_NAME` | Service identifier | No | sow_generator |
| `HOST` | Server host | No | 0.0.0.0 |
| `PORT` | Server port | No | 8080 |
| `AGENT_ENGINE_URI` | Agent Engine instance URI | Yes | - |
| `ARTIFACT_SERVICE_URI` | GCS bucket for artifacts | Yes | - |
| `SOW_TEMPLATE_GCS_URI` | GCS URI of SOW template | Yes | - |
| `LOG_LEVEL` | Logging verbosity | No | INFO |
| `SERVE_WEB_INTERFACE` | Enable ADK web UI | No | true |

### Setting Environment Variables

You can set environment variables in Cloud Run using:

```bash
gcloud run services update sow-generator \
  --region=us-central1 \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=your-project-id,AGENT_NAME=sow_generator"
```

### Using Secret Manager

For sensitive values like API keys:

```bash
# Create a secret
echo -n "your-secret-value" | gcloud secrets create secret-name --data-file=-

# Grant Cloud Run service account access
gcloud secrets add-iam-policy-binding secret-name \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Update Cloud Run service to use the secret
gcloud run services update sow-generator \
  --region=us-central1 \
  --set-secrets="AGENT_ENGINE_URI=agent-engine-uri:latest"
```

## Authentication

### Option 1: Default Service Account (Recommended for Cloud Run)

Cloud Run automatically provides a service account. Grant it necessary permissions:

```bash
# Get the service account email
SERVICE_ACCOUNT=$(gcloud run services describe sow-generator \
  --region=us-central1 \
  --format='value(spec.template.spec.serviceAccountName)')

# Grant Vertex AI permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/aiplatform.user"

# Grant Storage permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/storage.admin"
```

### Option 2: Custom Service Account

```bash
# Create a service account
gcloud iam service-accounts create sow-generator \
  --display-name="SOW Generator Service Account"

# Grant necessary roles
for role in "roles/aiplatform.user" "roles/storage.admin" "roles/logging.logWriter"; do
  gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:sow-generator@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="${role}"
done

# Deploy with custom service account
gcloud run services update sow-generator \
  --region=us-central1 \
  --service-account="sow-generator@${PROJECT_ID}.iam.gserviceaccount.com"
```

## Customization

### Cloud Build Substitutions

You can customize the deployment by passing substitution variables:

```bash
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=\
_SERVICE_NAME="sow-generator",\
_REGION="us-central1",\
_MEMORY="4Gi",\
_CPU="4",\
_MIN_INSTANCES="1",\
_MAX_INSTANCES="20"
```

Available substitutions:
- `_SERVICE_NAME`: Cloud Run service name (default: sow-generator)
- `_REGION`: Deployment region (default: us-central1)
- `_MEMORY`: Memory allocation (default: 2Gi)
- `_CPU`: CPU allocation (default: 2)
- `_MIN_INSTANCES`: Minimum instances (default: 0)
- `_MAX_INSTANCES`: Maximum instances (default: 10)
- `_TIMEOUT`: Request timeout (default: 300s)
- `_CONCURRENCY`: Max concurrent requests (default: 80)

## Testing the Deployment

After deployment, test the service:

```bash
# Get the service URL
SERVICE_URL=$(gcloud run services describe sow-generator \
  --region=us-central1 \
  --format='value(status.url)')

# Test health endpoint
curl ${SERVICE_URL}/health

# Test with ADK web interface (if enabled)
# Visit ${SERVICE_URL} in your browser
```

## Monitoring and Logs

### View Logs

```bash
# Stream logs
gcloud run services logs tail sow-generator \
  --region=us-central1

# View logs in Cloud Console
gcloud run services logs read sow-generator \
  --region=us-central1 \
  --limit=50
```

### Cloud Monitoring

The application automatically exports traces and metrics to Cloud Monitoring when deployed to Cloud Run.

Access in Cloud Console:
- **Logs**: Cloud Logging → Logs Explorer
- **Traces**: Cloud Trace
- **Metrics**: Cloud Run → Service Details

## Troubleshooting

### Common Issues

**1. Build fails with dependency errors**
```bash
# Ensure uv.lock is up to date
uv lock

# Commit changes and redeploy
git add uv.lock
git commit -m "Update dependencies"
```

**2. Service crashes on startup**
```bash
# Check logs for errors
gcloud run services logs tail sow-generator --region=us-central1

# Common causes:
# - Missing environment variables
# - Insufficient permissions
# - Invalid service account credentials
```

**3. Timeout errors**
```bash
# Increase timeout
gcloud run services update sow-generator \
  --region=us-central1 \
  --timeout=600s
```

**4. Out of memory errors**
```bash
# Increase memory allocation
gcloud run services update sow-generator \
  --region=us-central1 \
  --memory=4Gi
```

## Continuous Deployment

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - name: Deploy to Cloud Run
        run: |
          gcloud builds submit --config=cloudbuild.yaml
```

## Cleanup

To delete the deployed service:

```bash
# Delete Cloud Run service
gcloud run services delete sow-generator \
  --region=us-central1

# Delete Artifact Registry images (optional)
gcloud artifacts docker images delete \
  us-central1-docker.pkg.dev/${PROJECT_ID}/cloud-run-source-deploy/sow-generator \
  --delete-tags
```

## Support

For issues or questions:
1. Check application logs in Cloud Logging
2. Review Cloud Run service configuration
3. Verify service account permissions
4. Ensure all required APIs are enabled
