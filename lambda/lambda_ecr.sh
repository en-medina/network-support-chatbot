#!/bin/bash
set -euo pipefail

# Usage: ./zipfile.sh <source_folder>
SOURCE_FOLDER=$1
export AWS_PROFILE=en-medina-personal
export AWS_ACCOUNT_ID=783111403365
export AWS_REGION=us-east-1

cd "$SOURCE_FOLDER"

aws ecr get-login-password --region $AWS_REGION | podman login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

podman build --platform linux/amd64 -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$SOURCE_FOLDER-function:latest .
podman push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$SOURCE_FOLDER-function:latest

# deploy the function with the latest image
aws lambda update-function-code \
  --function-name message-$SOURCE_FOLDER \
  --image-uri $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$SOURCE_FOLDER-function:latest
