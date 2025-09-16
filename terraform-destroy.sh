#!/bin/bash

# Terraform Destroy Script for Chessaroo
# WARNING: This will destroy ALL infrastructure created by Terraform

set -e

echo "⚠️  DANGER: This will destroy all AWS infrastructure!"
echo "=============================================="
echo ""
echo "This action will:"
echo "• Delete the ECS cluster and service"
echo "• Remove the Application Load Balancer"
echo "• Delete the VPC and all networking components"
echo "• Remove ECR repository and container images"
echo "• Delete all associated resources"
echo ""

read -p "Are you sure you want to proceed? Type 'yes' to confirm: " -r
if [[ ! $REPLY == "yes" ]]; then
    echo "Destruction cancelled."
    exit 0
fi

echo ""
read -p "Last chance! Type 'DESTROY' to proceed: " -r
if [[ ! $REPLY == "DESTROY" ]]; then
    echo "Destruction cancelled."
    exit 0
fi

# Change to terraform directory
cd terraform

# Get current AWS region
AWS_REGION=$(aws configure get region || echo "us-west-2")

echo ""
echo "🔥 Destroying infrastructure..."
terraform destroy -var="aws_region=$AWS_REGION" -auto-approve

echo ""
echo "💥 All infrastructure has been destroyed!"
echo "   Your AWS resources have been cleaned up."