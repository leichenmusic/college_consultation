#!/bin/bash

# Production deployment script for 蕾拉酱的AI留学顾问
# Usage: ./deploy.sh [version]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default version if not provided
VERSION=${1:-$(date +"%Y%m%d-%H%M%S")}

echo -e "${BLUE}🚀 Starting production deployment...${NC}"
echo -e "${YELLOW}Version: ${VERSION}${NC}"

# Pre-deployment checks
echo -e "${BLUE}📋 Running pre-deployment checks...${NC}"

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${RED}❌ Not authenticated with gcloud. Please run 'gcloud auth login'${NC}"
    exit 1
fi

# Check if project is set
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ No project set. Please run 'gcloud config set project YOUR_PROJECT_ID'${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Project: ${PROJECT_ID}${NC}"

# Check required files
REQUIRED_FILES=("app.py" "main.py" "app.yaml" "requirements.txt" "static/images/layla_avatar.png")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Required file missing: ${file}${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ All required files present${NC}"

# Validate app.yaml
echo -e "${BLUE}🔍 Validating app.yaml...${NC}"
if ! gcloud app deploy app.yaml --dry-run --quiet > /dev/null 2>&1; then
    echo -e "${RED}❌ app.yaml validation failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ app.yaml is valid${NC}"

# Deploy to production
echo -e "${BLUE}🚀 Deploying to production...${NC}"
echo -e "${YELLOW}⚠️  This will deploy to: https://${PROJECT_ID}.appspot.com${NC}"

read -p "Continue with deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}❌ Deployment cancelled${NC}"
    exit 0
fi

# Deploy with version
echo -e "${BLUE}📦 Deploying version: ${VERSION}...${NC}"
gcloud app deploy \
    --version="${VERSION}" \
    --promote \
    --stop-previous-version \
    --verbosity=info

if [ $? -eq 0 ]; then
    echo -e "${GREEN}🎉 Deployment successful!${NC}"
    echo -e "${GREEN}🌐 Your app is live at: https://${PROJECT_ID}.appspot.com${NC}"
    echo -e "${BLUE}📊 View logs: gcloud app logs tail -s default${NC}"
    echo -e "${BLUE}📈 Monitor: https://console.cloud.google.com/appengine?project=${PROJECT_ID}${NC}"
    
    # Open the deployed app
    read -p "Open the app in browser? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gcloud app browse
    fi
else
    echo -e "${RED}❌ Deployment failed!${NC}"
    exit 1
fi
