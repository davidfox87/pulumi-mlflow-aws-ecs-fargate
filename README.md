# MLOps

FastAPI integration with MLFlow backend and model store

The stack takes a few minutes to launch the MLflow server on Fargate, with an S3 bucket and a MySQL database on RDS. The load balancer URI is outputs by pulumi when the MLFlow-server stack has been provisioned.

Run train.py

You can then use the load balancer URI to access the MLflow UI.

Just type the address of the load balancer in your web browser.

TODO:
1. provision ML-flow in aws ECS fargate
2. run train.py to register a model and then promote it to production
3. In jupyter, do some experimentation and hyperparameter tuning to find a better model, register the model
4. pull the latest model (labeled experiment 1) and the production model 
5. Compare the scores. If the latest model beats the production model score, then we branch and submit a pull request to merge with the main branch
6. trigger github actions workflow, if the changes pass unit and integration tests we will assign the production label to the new model