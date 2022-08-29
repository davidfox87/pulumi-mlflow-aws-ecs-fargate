aws ecr get-login-password --region us-west-1 | docker login --username AWS --password-stdin 880572800141.dkr.ecr.us-west-1.amazonaws.com

docker build -t lambda_container_test .
[ $? -eq 0 ] && docker tag lambda_container_test:latest 880572800141.dkr.ecr.us-west-1.amazonaws.com/lambda_container_test
[ $? -eq 0 ] && docker push 880572800141.dkr.ecr.us-west-1.amazonaws.com/lambda_container_test:latest
