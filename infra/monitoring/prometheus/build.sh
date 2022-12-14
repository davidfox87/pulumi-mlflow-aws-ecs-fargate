#!/bin/bash

aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 968467591626.dkr.ecr.us-west-2.amazonaws.com
[ $? -eq 0 ] && docker build -t prometheus .
[ $? -eq 0 ] && docker tag prometheus:latest 968467591626.dkr.ecr.us-west-2.amazonaws.com/prometheus:latest
[ $? -eq 0 ] && docker push 968467591626.dkr.ecr.us-west-2.amazonaws.com/prometheus:latest