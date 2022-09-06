#!/usr/bin/env bash

IMAGE_NAME=$1
AWS_ACCOUNT=880572800141
AWS_DEFAULT_REGION=us-west-1

aws ecr get-login-password --region us-west-1 | docker login --username AWS --password-stdin 880572800141.dkr.ecr.us-west-1.amazonaws.com

### ECR - build images and push to remote repository

echo "Building image: $IMAGE_NAME:latest"

docker build --rm -t $IMAGE_NAME:latest .

# tag and push image using latest
[ $? -eq 0 ] && docker tag $IMAGE_NAME:latest $AWS_ACCOUNT.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_NAME:latest
[ $? -eq 0 ] && docker push $AWS_ACCOUNT.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_NAME:latest

