aws ecr get-login-password --region us-west-1 | docker login --username AWS --password-stdin 880572800141.dkr.ecr.us-west-1.amazonaws.com

docker build -t mlflow_server .
[ $? -eq 0 ] && docker tag mlflow_server:latest 880572800141.dkr.ecr.us-west-1.amazonaws.com/mlflow_server:latest
[ $? -eq 0 ] && docker push 880572800141.dkr.ecr.us-west-1.amazonaws.com/mlflow_server:latest
