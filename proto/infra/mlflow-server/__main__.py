"""An AWS Python Pulumi program"""

from pulumi import export, ResourceOptions, Config, StackReference, Output
from pulumi_aws import s3
from backend_store import RDSDb, RDSDbArgs
from mlflowserver import MLFlowServer, MLFlowServerArgs

# Get config data
config = Config()
service_name = config.get('service_name') or 'mlflow-example'
db_name=config.get('db_name') or 'backend_store'
db_user=config.get('db_user') or 'david'
db_password=config.get_secret('db_password')

# reference the networking stack
networkingStack = StackReference(config.require('NetworkingStack'))


# Create an AWS resource (S3 Bucket)
artifact_bucket = s3.Bucket('mlflow-artifacts')

# Create a knowledge builder RDS MariaDB instance
backend_store = RDSDb(
     f'{service_name}-rds',
     RDSDbArgs(
          db_name=db_name,
          db_user=db_user,
          db_password=db_password,
          subnets=[networkingStack.get_output("public_subnet1"),
                    networkingStack.get_output("public_subnet2")
          ],
          security_group_ids=[networkingStack.get_output("rds_sg_id")]
     )
)


mlflow = MLFlowServer(
     f'{service_name}-mlflow-server',
     MLFlowServerArgs(
          vpc_id=networkingStack.get_output("vpc_id"),
          subnet_ids=[networkingStack.get_output("public_subnet1"),
                      networkingStack.get_output("public_subnet2"),
          ],
          security_group_ids=[networkingStack.get_output("ecs_sg_id"),
                            networkingStack.get_output("alb_sg_id")],
          db_host = backend_store.db.address,
          db_port = 3306,
          db_user = db_user,
          db_password = db_password,
          db_name = db_name,
          artifact_bucket = artifact_bucket.bucket,
     ),
     opts=ResourceOptions(depends_on=backend_store) # db needs to be up before knowledge builder can be provisioned.
)


# Export the name of the bucket
export('mlflow-artifacts_bucket_name', artifact_bucket.bucket)

web_url=Output.concat('http://', mlflow.alb.dns_name)
export('Web Service URL', web_url)
export('ECS Cluster Name', mlflow.cluster.name)