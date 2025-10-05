#!/bin/bash

# Terraform AWS Setup Script for BlunderLab
# This script will ensure the remote Terraform state backend exists and then deploy AWS infrastructure

set -e

echo "🚀 Setting up AWS for BlunderLab deployment with Terraform"
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
STATE_BUCKET=${TF_STATE_BUCKET:-blunderlab-tf-state}
STATE_LOCK_TABLE=${TF_STATE_LOCK_TABLE:-blunderlab-tf-locks}

echo "Account ID: $ACCOUNT_ID"
echo "Region: $REGION"
echo "State bucket: $STATE_BUCKET"
echo "State lock table: $STATE_LOCK_TABLE"
echo ""

# Ensure remote state bucket exists (idempotent)
echo "🔐 Ensuring Terraform remote state bucket exists..."
if aws s3api head-bucket --bucket "$STATE_BUCKET" 2>/dev/null; then
    echo "   ✅ Found $STATE_BUCKET"
else
    echo "   🪣 Creating S3 bucket $STATE_BUCKET"
    if [[ "$REGION" == "us-east-1" ]]; then
        aws s3api create-bucket --bucket "$STATE_BUCKET"
    else
        aws s3api create-bucket --bucket "$STATE_BUCKET" --region "$REGION" --create-bucket-configuration LocationConstraint="$REGION"
    fi

    echo "   🔒 Enabling bucket encryption and versioning"
    aws s3api put-bucket-encryption \
        --bucket "$STATE_BUCKET" \
        --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

    aws s3api put-bucket-versioning \
        --bucket "$STATE_BUCKET" \
        --versioning-configuration Status=Enabled

    aws s3api put-public-access-block \
        --bucket "$STATE_BUCKET" \
        --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
fi

# Ensure DynamoDB lock table exists (idempotent)
echo "🔐 Ensuring Terraform state lock table exists..."
if aws dynamodb describe-table --table-name "$STATE_LOCK_TABLE" >/dev/null 2>&1; then
    echo "   ✅ Found $STATE_LOCK_TABLE"
else
    echo "   🧱 Creating DynamoDB table $STATE_LOCK_TABLE"
    aws dynamodb create-table \
        --table-name "$STATE_LOCK_TABLE" \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST \
        --sse-specification Enabled=true,SSEType=KMS

    aws dynamodb wait table-exists --table-name "$STATE_LOCK_TABLE"
fi

# Change to terraform directory
cd terraform

# Initialize Terraform
echo "🔧 Initializing Terraform..."
terraform init -reconfigure

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
echo "1. Commit and push your changes to main so GitHub Actions can deploy."
echo "   (If you need a one-off manual deploy, run ./scripts/deploy.sh from a trusted machine.)"
echo ""
echo "2. Once the workflow completes, your app will be available at:"
echo "   $ALB_URL"
echo ""
echo "💡 Note: The first deployment may take a few minutes to show up"
echo "   because the ECS service needs to pull and start the container."

