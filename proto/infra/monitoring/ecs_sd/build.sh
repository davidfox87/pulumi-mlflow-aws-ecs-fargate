#!/bin/bash

aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 968467591626.dkr.ecr.us-west-2.amazonaws.com
[ $? -eq 0 ] && docker build -t ecs_service_discovery .
[ $? -eq 0 ] && docker tag ecs_service_discovery:latest 968467591626.dkr.ecr.us-west-2.amazonaws.com/ecs_service_discovery:latest
[ $? -eq 0 ] && docker push docker push 968467591626.dkr.ecr.us-west-2.amazonaws.com/ecs_service_discovery:latest
