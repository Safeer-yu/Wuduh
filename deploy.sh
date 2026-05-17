#!/bin/bash
set -e  # stop if any command fails

AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="825765383874"
ECR_REPO="wuduh"
ECS_CLUSTER="wuduh-cluster"
ECS_SERVICE="wuduh-service"
IMAGE_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest"

echo "Building Docker image..."
docker build -t $ECR_REPO .

echo "Authenticating with ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

echo "Tagging image..."
docker tag $ECR_REPO:latest $IMAGE_URI

echo " Pushing to ECR..."
docker push $IMAGE_URI

echo "Deploying to ECS..."
aws ecs update-service \
    --cluster $ECS_CLUSTER \
    --service $ECS_SERVICE \
    --force-new-deployment \
    --desired-count 1 \
    --region $AWS_REGION

echo "Deployment complete — Wuduh is live!"
echo "Wait ~2 minutes for the new container to start"