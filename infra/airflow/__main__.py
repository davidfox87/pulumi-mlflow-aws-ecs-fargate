
from pulumi import export, ResourceOptions, Config, StackReference, Output
import pulumi_aws as aws
from airflow import Airflow, AirflowArgs

# Get config data
config = Config()
service_name = config.get('service_name') or 'mlops'


# reference the networking stack
networkingStack = StackReference(config.require('NetworkingStack'))



default = aws.rds.Instance("metadata-db",
    allocated_storage=20,
    engine="postgres",
    engine_version="10.6",
    instance_class="db.t3.micro",
    name="airflow",
    parameter_group_name="default.mysql5.7",
    password="password",
    skip_final_snapshot=True,
    publicly_accessible=True,
    username="airflow",
    vpc_security_group_ids=[networkingStack.get_output("postgres_public_sg")],
    db_subnet_group_name=[networkingStack.get_output("public_subnet1"),
                      networkingStack.get_output("public_subnet2"),
     ]
)


mlflow = Airflow(
     f'{service_name}-airflow',
     AirflowArgs(
          vpc_id=networkingStack.get_output("vpc_id"),
          subnet_ids=[networkingStack.get_output("public_subnet1"),
                      networkingStack.get_output("public_subnet2"),
          ],
          security_group_ids=[networkingStack.get_output("web_server_ecs_internal_sg")],
          alb_arn=networkingStack.get_output("alb_arn")
     ) 
)

