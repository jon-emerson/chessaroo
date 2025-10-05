#!/bin/bash

# Terraform ECS Deployment Script
# Usage: ./scripts/deploy.sh

set -e

# Resolve deployment configuration either from environment or Terraform outputs
USED_TERRAFORM=false

if [ -n "$ECR_REPOSITORY_URL" ] && [ -n "$ECS_CLUSTER_NAME" ] && [ -n "$ECS_SERVICE_NAME" ]; then
    echo "🚀 Using deployment configuration from environment variables"
    ECR_URI="$ECR_REPOSITORY_URL"
    CLUSTER_NAME="$ECS_CLUSTER_NAME"
    SERVICE_NAME="$ECS_SERVICE_NAME"
    ALB_URL=${LOAD_BALANCER_URL:-""}
else
    echo "🚀 Getting deployment configuration from Terraform outputs..."
    cd terraform
    ECR_URI=$(terraform output -raw ecr_repository_url 2>/dev/null || echo "")
    CLUSTER_NAME=$(terraform output -raw cluster_name 2>/dev/null || echo "")
    SERVICE_NAME=$(terraform output -raw service_name 2>/dev/null || echo "")
    ALB_URL=$(terraform output -raw load_balancer_url 2>/dev/null || echo "")

    if [ -z "$ECR_URI" ] || [ -z "$CLUSTER_NAME" ] || [ -z "$SERVICE_NAME" ]; then
        echo "❌ Deployment configuration not available. Set ECR_REPOSITORY_URL, ECS_CLUSTER_NAME, and ECS_SERVICE_NAME or run terraform first."
        exit 1
    fi

    cd ..
    USED_TERRAFORM=true
fi

AWS_REGION=${AWS_REGION:-$(aws configure get region 2>/dev/null || echo "us-west-2")}
PROJECT_NAME="chessaroo"

echo "ECR Repository: $ECR_URI"
echo "ECS Cluster: $CLUSTER_NAME"
echo "ECS Service: $SERVICE_NAME"
echo "AWS Region: $AWS_REGION"
echo ""

# Build and tag Docker image
echo "🐳 Building Docker image..."
docker build --platform linux/amd64 -t $PROJECT_NAME .

# Tag for ECR
docker tag $PROJECT_NAME:latest $ECR_URI:latest

# Login to ECR
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin $ECR_URI

# Push to ECR
echo "📤 Pushing image to ECR..."
docker push $ECR_URI:latest

# Run database migrations inside the VPC using a one-off ECS task
echo "🗄️ Starting database migration task on ECS..."
SERVICE_DESC=$(aws ecs describe-services --cluster "$CLUSTER_NAME" --services "$SERVICE_NAME" --region "$AWS_REGION")

if [ -z "$SERVICE_DESC" ]; then
    echo "❌ Unable to describe ECS service $SERVICE_NAME"
    exit 1
fi

TASK_DEF_ARN=$(python3 -c 'import json,sys; data=json.loads(sys.stdin.read()); services=data.get("services", []); print(services[0]["taskDefinition"] if services else "")' <<< "$SERVICE_DESC")

if [ -z "$TASK_DEF_ARN" ]; then
    echo "❌ Could not determine task definition for service $SERVICE_NAME"
    exit 1
fi

TASK_DEF_DESC=$(aws ecs describe-task-definition --task-definition "$TASK_DEF_ARN" --region "$AWS_REGION")
CONTAINER_NAME=$(python3 -c 'import json,sys; data=json.loads(sys.stdin.read()); containers=data.get("taskDefinition", {}).get("containerDefinitions", []); print(containers[0]["name"] if containers else "")' <<< "$TASK_DEF_DESC")

if [ -z "$CONTAINER_NAME" ]; then
    echo "❌ Could not determine container name from task definition"
    exit 1
fi

SUBNETS=$(python3 -c 'import json,sys; data=json.loads(sys.stdin.read()); svc=data.get("services", []); cfg=svc[0].get("networkConfiguration", {}).get("awsvpcConfiguration", {}) if svc else {}; print(",".join(cfg.get("subnets", [])))' <<< "$SERVICE_DESC")
SECURITY_GROUPS=$(python3 -c 'import json,sys; data=json.loads(sys.stdin.read()); svc=data.get("services", []); cfg=svc[0].get("networkConfiguration", {}).get("awsvpcConfiguration", {}) if svc else {}; print(",".join(cfg.get("securityGroups", [])))' <<< "$SERVICE_DESC")
ASSIGN_PUBLIC_IP=$(python3 -c 'import json,sys; data=json.loads(sys.stdin.read()); svc=data.get("services", []); cfg=svc[0].get("networkConfiguration", {}).get("awsvpcConfiguration", {}) if svc else {}; print(cfg.get("assignPublicIp", "DISABLED"))' <<< "$SERVICE_DESC")

if [ -z "$SUBNETS" ] || [ -z "$SECURITY_GROUPS" ]; then
    echo "❌ Missing subnet or security group configuration on the ECS service"
    exit 1
fi

NETWORK_CONFIGURATION="awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SECURITY_GROUPS],assignPublicIp=$ASSIGN_PUBLIC_IP}"

export CONTAINER_NAME
MIGRATION_OVERRIDES=$(python3 - <<'PY'
import json
import os

container_name = os.environ["CONTAINER_NAME"]

overrides = {
    "containerOverrides": [
        {
            "name": container_name,
            "command": ["python3", "-m", "flask", "db", "upgrade"],
            "environment": [
                {"name": "FLASK_APP", "value": "backend.app:create_app"},
                {"name": "FLASK_RUN_FROM_CLI", "value": "true"}
            ]
        }
    ]
}

print(json.dumps(overrides))
PY
)
unset CONTAINER_NAME

echo "   • Launching one-off task from $TASK_DEF_ARN"
RUN_TASK_OUTPUT=$(aws ecs run-task \
    --cluster "$CLUSTER_NAME" \
    --launch-type FARGATE \
    --task-definition "$TASK_DEF_ARN" \
    --count 1 \
    --started-by "db-migration-$(date +%s)" \
    --network-configuration "$NETWORK_CONFIGURATION" \
    --overrides "$MIGRATION_OVERRIDES" \
    --region "$AWS_REGION")

FAILURE_COUNT=$(python3 -c 'import json,sys; data=json.loads(sys.stdin.read()); print(len(data.get("failures", [])))' <<< "$RUN_TASK_OUTPUT")

if [ "$FAILURE_COUNT" != "0" ]; then
    python3 -c 'import json,sys; data=json.loads(sys.stdin.read()); fail=data.get("failures", []); [print(f"❌ Migration task request failed before start: {item.get(\"reason\", \"unknown\")} ({item.get(\"arn\", \"no-arn\")})") for item in fail]' <<< "$RUN_TASK_OUTPUT"
    exit 1
fi

TASK_ARN=$(python3 -c 'import json,sys; data=json.loads(sys.stdin.read()); tasks=data.get("tasks", []); print(tasks[0]["taskArn"] if tasks else "")' <<< "$RUN_TASK_OUTPUT")

if [ -z "$TASK_ARN" ]; then
    echo "❌ Migration task ARN could not be determined"
    exit 1
fi

echo "⏳ Waiting for migration task ($TASK_ARN) to finish..."
aws ecs wait tasks-stopped --cluster "$CLUSTER_NAME" --tasks "$TASK_ARN" --region "$AWS_REGION"

TASK_DETAILS=$(aws ecs describe-tasks --cluster "$CLUSTER_NAME" --tasks "$TASK_ARN" --region "$AWS_REGION")

EXIT_CODE=$(python3 -c 'import json,sys; data=json.loads(sys.stdin.read()); tasks=data.get("tasks", []); containers=tasks[0].get("containers", []) if tasks else []; print(containers[0].get("exitCode", 1) if containers else 1)' <<< "$TASK_DETAILS")
STOP_REASON=$(python3 -c 'import json,sys; data=json.loads(sys.stdin.read()); tasks=data.get("tasks", []); print(tasks[0].get("stoppedReason", "")) if tasks else print("")' <<< "$TASK_DETAILS")
CONTAINER_REASON=$(python3 -c 'import json,sys; data=json.loads(sys.stdin.read()); tasks=data.get("tasks", []); containers=tasks[0].get("containers", []) if tasks else []; print(containers[0].get("reason", "")) if containers else print("")' <<< "$TASK_DETAILS")

if [ "$EXIT_CODE" != "0" ]; then
    if [ "$EXIT_CODE" = "72" ]; then
        echo "🛑 Migration container exited because the runtime guard rejected a non-container environment."
        echo "   Ensure the task has ECS metadata available or set ALLOW_NON_CONTAINER=1 only if you intentionally bypass the guard."
    elif [ "$EXIT_CODE" = "2" ]; then
        echo "🛑 Migration container exited with code 2 — likely an import or application startup failure before Alembic ran."
    else
        echo "❌ Migration task failed (exit code $EXIT_CODE)"
    fi
    [ -n "$STOP_REASON" ] && echo "   Task stop reason: $STOP_REASON"
    [ -n "$CONTAINER_REASON" ] && echo "   Container reason: $CONTAINER_REASON"
    exit 1
fi

echo "✅ Database migrations completed successfully."

# Force new deployment (this will use the updated image)
echo "🚀 Deploying to ECS..."
aws ecs update-service --cluster "$CLUSTER_NAME" --service "$SERVICE_NAME" --force-new-deployment --region "$AWS_REGION"
aws ecs wait services-stable --cluster "$CLUSTER_NAME" --services "$SERVICE_NAME" --region "$AWS_REGION"

if [ "$USED_TERRAFORM" = true ]; then
    cd terraform
    ALB_URL=$(terraform output -raw load_balancer_url 2>/dev/null || echo "")
    cd ..
fi

echo ""
echo "✅ Deployment complete!"
if [ -n "$ALB_URL" ] && [[ "$ALB_URL" != *"***"* ]]; then
    echo "🌐 Load balancer endpoint: $ALB_URL"
fi
echo "⏳ It may take a few minutes for the new version to be available."
