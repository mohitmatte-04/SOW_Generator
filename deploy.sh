#!/bin/bash

# SOW Generator - Cloud Run Deployment Script
# This script deploys the SOW Generator application to Google Cloud Run

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
SERVICE_NAME="${SERVICE_NAME:-sow-generator}"
REGION="${REGION:-us-central1}"
MEMORY="${MEMORY:-2Gi}"
CPU="${CPU:-2}"
MIN_INSTANCES="${MIN_INSTANCES:-0}"
MAX_INSTANCES="${MAX_INSTANCES:-10}"
TIMEOUT="${TIMEOUT:-300s}"

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_info "Checking prerequisites..."

if ! command_exists gcloud; then
    print_error "gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

if ! command_exists docker; then
    print_error "docker not found. Please install Docker."
    exit 1
fi

print_success "Prerequisites check passed"

# Get current project
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    print_error "No Google Cloud project configured. Run: gcloud config set project PROJECT_ID"
    exit 1
fi

print_info "Using Google Cloud Project: ${PROJECT_ID}"
print_info "Service Name: ${SERVICE_NAME}"
print_info "Region: ${REGION}"

# Prompt for confirmation
read -p "$(echo -e ${YELLOW}Continue with deployment? [y/N]:${NC} )" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Deployment cancelled"
    exit 0
fi

# Enable required APIs
print_info "Enabling required Google Cloud APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    slides.googleapis.com \
    drive.googleapis.com \
    --project="${PROJECT_ID}"

print_success "APIs enabled"

# Create Artifact Registry repository if it doesn't exist
print_info "Checking Artifact Registry repository..."
ARTIFACT_REPO="cloud-run-source-deploy"

if ! gcloud artifacts repositories describe "${ARTIFACT_REPO}" \
    --location="${REGION}" \
    --project="${PROJECT_ID}" >/dev/null 2>&1; then

    print_info "Creating Artifact Registry repository..."
    gcloud artifacts repositories create "${ARTIFACT_REPO}" \
        --repository-format=docker \
        --location="${REGION}" \
        --project="${PROJECT_ID}"

    print_success "Artifact Registry repository created"
else
    print_success "Artifact Registry repository exists"
fi

# Submit build to Cloud Build
print_info "Submitting build to Cloud Build..."
gcloud builds submit \
    --config=cloudbuild.yaml \
    --substitutions=_SERVICE_NAME="${SERVICE_NAME}",_REGION="${REGION}",_MEMORY="${MEMORY}",_CPU="${CPU}",_MIN_INSTANCES="${MIN_INSTANCES}",_MAX_INSTANCES="${MAX_INSTANCES}",_TIMEOUT="${TIMEOUT}" \
    --project="${PROJECT_ID}"

print_success "Build and deployment completed successfully!"

# Get service URL
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
    --region="${REGION}" \
    --project="${PROJECT_ID}" \
    --format='value(status.url)' 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
    print_success "Service deployed at: ${SERVICE_URL}"
    print_info "Health check: ${SERVICE_URL}/health"
else
    print_warning "Could not retrieve service URL"
fi

echo ""
print_info "Deployment complete!"
