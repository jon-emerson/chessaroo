#!/bin/bash

# Terraform ECS Deployment Script
# Usage: ./scripts/deploy.sh

set -e

# Change to terraform directory for getting outputs
cd terraform

# Get configuration from Terraform outputs
echo "🚀 Getting deployment configuration..."

ECR_URI=$(terraform output -raw ecr_repository_url 2>/dev/null || echo "")
CLUSTER_NAME=$(terraform output -raw cluster_name 2>/dev/null || echo "")
SERVICE_NAME=$(terraform output -raw service_name 2>/dev/null || echo "")

if [ -z "$ECR_URI" ] || [ -z "$CLUSTER_NAME" ] || [ -z "$SERVICE_NAME" ]; then
    echo "❌ Terraform outputs not available. Please run ./terraform-setup.sh first."
    exit 1
fi

AWS_REGION=$(aws configure get region || echo "us-west-2")
PROJECT_NAME="chessaroo"

echo "ECR Repository: $ECR_URI"
echo "ECS Cluster: $CLUSTER_NAME"
echo "ECS Service: $SERVICE_NAME"
echo ""

# Change back to project root
cd ..

# Build and tag Docker image
echo "🐳 Building Docker image..."
docker build --platform linux/amd64 -t $PROJECT_NAME .

# Tag for ECR
docker tag $PROJECT_NAME:latest $ECR_URI:latest

# Login to ECR
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI

# Push to ECR
echo "📤 Pushing image to ECR..."
docker push $ECR_URI:latest

# Force new deployment (this will use the updated image)
echo "🚀 Deploying to ECS..."
aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --force-new-deployment

# Get the load balancer URL
cd terraform
ALB_URL=$(terraform output -raw load_balancer_url 2>/dev/null || echo "")

echo ""
echo "✅ Deployment complete!"
if [ -n "$ALB_URL" ]; then
    echo "🌐 Your app will be available at: $ALB_URL"
fi
echo "⏳ It may take a few minutes for the new version to be available."