# MLOps

FastAPI integration with MLFlow backend and model store
https://github.com/zademn/mnist-mlops-learning/blob/master/backend/main.py

The stack takes a few minutes to launch the MLflow server on Fargate, with an S3 bucket and a MySQL database on RDS. The load balancer URI is outputs by pulumi when the MLFlow-server stack has been provisioned.

Run train.py

You can then use the load balancer URI to access the MLflow UI.

Just type the address of the load balancer in your web browser.
# Tracking Jupyter runs with MLflow in your local environment

You now have a remote MLflow tracking server running accessible through a REST API via the load balancer URI.

You can use the MLflow Tracking API to log parameters, metrics, and models when running your ML project in Jupyter. For this you need to install the MLflow library when running your code in Jupyter and set the remote tracking URI to be your load balancer address.

The following Python API command allows you to point your code running on SageMaker to your MLflow remote server:

```
import mlflow
mlflow.set_tracking_uri('<YOUR LOAD BALANCER URI>')
```