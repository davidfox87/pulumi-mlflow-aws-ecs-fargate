import json
from typing import List

import pulumi_aws as aws
from pulumi import ComponentResource, Output, ResourceOptions


class AirflowArgs:
    """_summary_
    """

    def __init__(
        self,
        vpc_id=None,
        subnet_ids: List[str] = None,  # array of subnet IDs
        security_group_ids: str = None,
        alb_arn: str = None

    ):
        self.vpc_id = vpc_id
        self.subnet_ids = subnet_ids
        self.security_group_ids = security_group_ids
        self.alb_arn = alb_arn


class Airflow(ComponentResource):
    """_summary_

    Args:
        ComponentResource (_type_): _description_
    """

    def __init__(
        self, name: str, args: AirflowArgs, opts: ResourceOptions = None
    ):

        super().__init__("Airflow-server", name, {}, opts)


        # Create an ECS cluster to run a container-based service.
        self.cluster = aws.ecs.Cluster('ecs',
            opts=ResourceOptions(parent=self)
        )

        atg = aws.lb.TargetGroup(
            "airflowflow-tg",
            port=5000, 
            protocol="HTTP",
            target_type="ip",
            vpc_id=args.vpc_id,
            health_check=aws.lb.TargetGroupHealthCheckArgs(
                healthy_threshold=2,
                interval=5,
                timeout=4,
                protocol='HTTP',
                matcher='200-399'
            ),
            opts=ResourceOptions(parent=self),
        )

        wl = aws.lb.Listener(
            "airflow-listener",
            protocol="HTTP",
            load_balancer_arn=args.alb_arn,
            port=80,  
            default_actions=[aws.lb.ListenerDefaultActionArgs(
                type='forward',
                target_group_arn=atg.arn, # forward to target group on port 5000
            )],
            opts=ResourceOptions(parent=self)
        )

        # create a task execution IAM role
        # Create an IAM role that can be used by our service's task.
        app_exec_role = aws.iam.Role(
            "exec-role",
            assume_role_policy=json.dumps(
                {
                    "Version": "2008-10-17",
                    "Statement": [
                        {
                            "Sid": "",
                            "Effect": "Allow",
                            "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                            "Action": "sts:AssumeRole",
                        }
                    ],
                }
            ),
            
            opts=ResourceOptions(parent=self),
        )
        # Attaching execution permissions to the exec role
        exec_policy_attachment = aws.iam.RolePolicyAttachment("app-exec-policy", 
                                                                role=app_exec_role.name,
                                                                policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
                                                                opts=ResourceOptions(parent=self),
                                )


        # Creating an IAM role used by Fargate to manage tasks
        app_task_role = aws.iam.Role("app-task-role",
                                     assume_role_policy="""{
                "Version": "2012-10-17",
                "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {
                        "Service": "ecs-tasks.amazonaws.com"
                    },
                    "Effect": "Allow",
                    "Sid": ""
                }]
            }"""
        )

        # Attaching execution permissions to the task role
        task_policy_attachment = aws.iam.RolePolicyAttachment("app-access-policy",
                                                              role=app_task_role.name,
                                                              policy_arn=aws.iam.ManagedPolicy.AMAZON_ECS_FULL_ACCESS
                                                              )

        self.task_definition = aws.ecs.TaskDefinition("webserver,
                                                        family="airflow",
                                                        cpu="256",
                                                        memory="128",
                                                        

        
        ")
        # # Creating a task definition for the Flask instance.
        # self.task_definition = aws.ecs.TaskDefinition("mlflow-server",
        #         family="mlflow-server",
        #         cpu="256",
        #         memory="512",
        #         network_mode="awsvpc",
        #         requires_compatibilities=["FARGATE"],
        #         execution_role_arn=app_exec_role.arn,
        #         task_role_arn=app_task_role.arn,
        #         container_definitions=Output.all(artifact_bucket_name=args.artifact_bucket,
        #                                         db_host=args.db_host,
        #                                         db_name=args.db_name,
        #                                         db_port=3306,
        #                                         db_username=args.db_user,
        #                                         db_password=args.db_password).apply(
        #                                             lambda args_:
        #                                             json.dumps([{
        #                                                 "name": "mlflow_server",
        #                                                 "image": "880572800141.dkr.ecr.us-west-1.amazonaws.com/mlflow_server:latest",
        #                                                 "memory": 512,
        #                                                 "essential": True,
        #                                                 "portMappings": [{
        #                                                     "containerPort": 5000,
        #                                                     "hostPort": 5000,
        #                                                     "protocol": "tcp"
        #                                                 }],
        #                                                 "environment": [{'name' : 'BUCKET', 'value': f"s3://{args_['artifact_bucket_name']}"},
        #                                                                 {'name' : 'HOST', 'value' : args_['db_host'] },
        #                                                                 {'name' : 'PORT', 'value' : str(args_['db_port'])},
        #                                                                 {'name' : 'DATABASE', 'value' : args_['db_name']},
        #                                                                 {'name' : 'USERNAME', 'value': args_['db_username']},
        #                                                                 {'name' : 'PASSWORD', 'value': args_['db_password']}
        #                                                 ],
        #                                                 "logConfiguration": {
        #                                                     "logDriver": "awslogs",
        #                                                     "options": {
        #                                                         "awslogs-group": "/mlflow/test",
        #                                                         "awslogs-region": aws.get_region().name,
        #                                                         "awslogs-stream-prefix": "mlflow",
        #                                                         "awslogs-create-group": "true"
        #                                                     },
        #                                                 },
        #                                             }])
        #                                         )
        # )
        

        # self.service = aws.ecs.Service('app-svc',
        #     cluster=self.cluster.arn,
        #     desired_count=1,
        #     launch_type='FARGATE',
        #     task_definition=self.task_definition.arn,
        #     network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(
        #         assign_public_ip=True,
        #         subnets=args.subnet_ids,
        #         security_groups=args.security_group_ids
        #     ),
        #     load_balancers=[aws.ecs.ServiceLoadBalancerArgs(
        #         target_group_arn=atg.arn,
        #         container_name='mlflow_server',
        #         container_port=5000,
        #     )],
            
        #     opts=ResourceOptions(
        #         depends_on=[wl], parent=self),
        # )

        self.register_outputs({})
