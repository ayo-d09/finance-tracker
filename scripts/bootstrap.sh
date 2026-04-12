#!/bin/bash
set -e

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
REGION="us-east-1"
APP_NAME="finance-tracker"
GITHUB_ORG="ayo-d09"
GITHUB_REPO="finance-tracker"
BUCKET_NAME="${APP_NAME}-tfstate-${AWS_ACCOUNT_ID}"

# S3 bucket for Terraform state
aws s3api create-bucket \
  --bucket ${BUCKET_NAME} \
  --region ${REGION}

aws s3api put-bucket-versioning \
  --bucket ${BUCKET_NAME} \
  --versioning-configuration Status=Enabled

# DynamoDB table for state locking
aws dynamodb create-table \
  --table-name ${APP_NAME}-tfstate-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region ${REGION}

# ECR repository
aws ecr describe-repositories --repository-names ${APP_NAME} --region ${REGION} 2>/dev/null || \
aws ecr create-repository --repository-name ${APP_NAME} --region ${REGION}

# OIDC provider
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1

# IAM role for GitHub Actions
aws iam create-role \
  --role-name ${APP_NAME}-github-actions-role \
  --assume-role-policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Federated\":\"arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com\"},\"Action\":\"sts:AssumeRoleWithWebIdentity\",\"Condition\":{\"StringLike\":{\"token.actions.githubusercontent.com:sub\":\"repo:${GITHUB_ORG}/${GITHUB_REPO}:*\"}}}]}"

# Attach policies
aws iam attach-role-policy \
  --role-name ${APP_NAME}-github-actions-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser

aws iam attach-role-policy \
  --role-name ${APP_NAME}-github-actions-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonECS_FullAccess

aws iam attach-role-policy \
  --role-name ${APP_NAME}-github-actions-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-role-policy \
  --role-name ${APP_NAME}-github-actions-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

echo "Bootstrap complete"
echo "Add this to GitHub secrets as AWS_ROLE_ARN:"
echo "arn:aws:iam::${AWS_ACCOUNT_ID}:role/${APP_NAME}-github-actions-role"