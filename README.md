# MLOps 

This is demo of an MLOps platform. It serves the infrastructure using Pulumi and python in the proto/infra subfolder.
The stack takes a few minutes to launch the MLflow server on ECS Fargate, with an S3 bucket to store the model artifacts and a MySQL database on RDS to store track the results of experiments. The load balancer URI is output by pulumi when the MLFlow-server stack has been provisioned. This URI is used by data scientists when specifying the TRACKING_URI of the MLflow server in a local Jupyter notebook.

We can first run ds_experiments/train.py to register a model with MLflow and also promote it to production.

Then a data scientist working in a Jupyter notebook can experiment with hyperparameter tuning of the same algorithm or compare across algorithms. The can pull the model artifact from MLflow that has been labeled with "Production" and compare it with their new models just discovered.

If their new model beats the score of the model in production, then they can create a new git branch, push to Github, and submit a pull request (PR). Submitting a pull request will trigger the CI/CD pipeline using github actions workflow. 


Note: 
- To access the MLflow server from your local Jupyter do mlflow.set_tracking_uri(<LOAD_BALANCER_URI>)
- To access the MLflow UI, just type the address of the load balancer in your web browser.

# ML Pipelines in the cloud
- playing with Airflow DAGs and AWS lambda functions
- playing with Kubeflow pipelines running in EKS


Below is a picture of the basic MLOps setup that supports both model experimentation. Next step is to deploy the production model on an ECS fargate cluster:

![MLOps platform](mlops.png)

The picture below is the intended design for the workflow orchestration of the ML pipeline in the cloud. Currently airflow is only running locally in docker-compose and i will be testing the ability to invoke Lambda functions from this local DAG workflow.


![MLOps workflow orchestration](airflow.png)


