#!/bin/bash

# AWS Setup Script for Chessaroo
# This script will guide you through setting up AWS from scratch

set -e

echo "🚀 Setting up AWS for Chessaroo deployment"
echo "=================================================="

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
REGION=$(aws configure get region || echo "us-east-1")

echo "Account ID: $ACCOUNT_ID"
echo "Region: $REGION"
echo ""

# Deploy CloudFormation stack
STACK_NAME="chessaroo-infrastructure"

echo "🏗️  Creating AWS infrastructure with CloudFormation..."
echo "Stack name: $STACK_NAME"

if aws cloudformation describe-stacks --stack-name $STACK_NAME &> /dev/null; then
    echo "Stack already exists. Updating..."
    aws cloudformation update-stack \
        --stack-name $STACK_NAME \
        --template-body file://aws-infrastructure.yml \
        --capabilities CAPABILITY_IAM
else
    echo "Creating new stack..."
    aws cloudformation create-stack \
        --stack-name $STACK_NAME \
        --template-body file://aws-infrastructure.yml \
        --capabilities CAPABILITY_IAM
fi

echo "⏳ Waiting for stack to complete (this may take 5-10 minutes)..."
aws cloudformation wait stack-create-complete --stack-name $STACK_NAME || \
aws cloudformation wait stack-update-complete --stack-name $STACK_NAME

echo "✅ Infrastructure created successfully!"

# Get outputs
ECR_URI=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`ECRRepositoryURI`].OutputValue' \
    --output text)

ALB_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerURL`].OutputValue' \
    --output text)

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
echo "   ./deploy.sh"
echo ""
echo "2. Your app will be available at:"
echo "   $ALB_URL"
echo ""
echo "💡 Note: The first deployment may take a few minutes to show up"
echo "   because the ECS service needs to pull and start the container."