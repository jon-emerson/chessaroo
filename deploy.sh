#!/bin/bash

# AWS ECS Deployment Script
# Usage: ./deploy.sh

set -e

# Configuration
STACK_NAME="chessaroo-infrastructure"
PROJECT_NAME="chessaroo"

# Get configuration from CloudFormation stack
echo "🚀 Getting deployment configuration..."

ECR_URI=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`ECRRepositoryURI`].OutputValue' \
    --output text)

CLUSTER_NAME=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`ClusterName`].OutputValue' \
    --output text)

SERVICE_NAME=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`ServiceName`].OutputValue' \
    --output text)

AWS_REGION=$(aws configure get region || echo "us-east-1")

echo "ECR Repository: $ECR_URI"
echo "ECS Cluster: $CLUSTER_NAME"
echo "ECS Service: $SERVICE_NAME"
echo ""

# Build and tag Docker image
echo "🐳 Building Docker image..."
docker build -t $PROJECT_NAME .

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
ALB_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerURL`].OutputValue' \
    --output text)

echo ""
echo "✅ Deployment complete!"
echo "🌐 Your app will be available at: $ALB_URL"
echo "⏳ It may take a few minutes for the new version to be available."