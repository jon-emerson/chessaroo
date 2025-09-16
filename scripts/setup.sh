#!/bin/bash

# Terraform AWS Setup Script for Chessaroo
# This script will deploy AWS infrastructure using Terraform

set -e

echo "🚀 Setting up AWS for Chessaroo deployment with Terraform"
echo "========================================================"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI is not configured. Let's set it up!"
    echo ""
    echo "You'll need to:"
    echo "1. Create an AWS account at https://aws.amazon.com if you don't have one"
    echo "2. Create an IAM user with programmatic access"
    echo "3. Get your Access Key ID and Secret Access Key"
    echo ""
    echo "Run: aws configure"
    echo "Enter your credentials when prompted"
    exit 1
fi

echo "✅ AWS CLI is configured"

# Get current AWS account and region
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region || echo "us-west-2")

echo "Account ID: $ACCOUNT_ID"
echo "Region: $REGION"
echo ""

# Change to terraform directory
cd terraform

# Initialize Terraform
echo "🔧 Initializing Terraform..."
terraform init

# Validate Terraform configuration
echo "🔍 Validating Terraform configuration..."
terraform validate

# Plan Terraform deployment
echo "📋 Planning Terraform deployment..."
terraform plan -var="aws_region=$REGION"

# Ask for confirmation
echo ""
read -p "Do you want to apply these changes? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

# Apply Terraform configuration
echo "🏗️  Applying Terraform configuration..."
terraform apply -var="aws_region=$REGION" -auto-approve

echo "✅ Infrastructure created successfully!"

# Get outputs
ECR_URI=$(terraform output -raw ecr_repository_url)
ALB_URL=$(terraform output -raw load_balancer_url)

echo ""
echo "🎉 Setup complete! Here's what was created:"
echo "==========================================="
echo "• VPC with public subnets"
echo "• Application Load Balancer"
echo "• ECS Cluster with Fargate"
echo "• ECR Repository: $ECR_URI"
echo "• Security groups and IAM roles"
echo ""
echo "📋 Next steps:"
echo "1. Build and push your Docker image:"
echo "   ./scripts/deploy.sh"
echo ""
echo "2. Your app will be available at:"
echo "   $ALB_URL"
echo ""
echo "💡 Note: The first deployment may take a few minutes to show up"
echo "   because the ECS service needs to pull and start the container."