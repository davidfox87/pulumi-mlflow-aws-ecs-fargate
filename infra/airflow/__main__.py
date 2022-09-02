
from pulumi import export, ResourceOptions, Config, StackReference, Output
from pulumi_aws import s3
from airflow import Airflow, AirflowArgs

# Get config data
config = Config()
service_name = config.get('service_name') or 'mlops'


# reference the networking stack
networkingStack = StackReference(config.require('NetworkingStack'))



mlflow = Airflow(
     f'{service_name}-airflow',
     AirflowArgs(
          vpc_id=networkingStack.get_output("vpc_id"),
          subnet_ids=[networkingStack.get_output("public_subnet1"),
                      networkingStack.get_output("public_subnet2"),
          ],
          security_group_ids=[networkingStack.get_output("ecs_sg_id")],
          alb_arn=networkingStack.get_output("alb_arn")
     ) 
)

