import json
from typing import List

import pulumi_aws as aws
from pulumi import ComponentResource, Output, ResourceOptions


class PrometheusArgs:
    """_summary_
    """

    def __init__(
        self,
        vpc_id=None,
        subnet_ids: List[str] = None,  # array of subnet IDs
        sg_groups: list[str] = None,
        ecs_cluster_arn: str = None,
    ):
        self.vpc_id = vpc_id
        self.subnet_ids = subnet_ids
        self.sg_groups = sg_groups
        self.ecs_cluster_arn = ecs_cluster_arn



class Prometheus(ComponentResource):
    """_summary_

    Args:
        ComponentResource (_type_): _description_
    """

    def __init__(
        self, name: str, args: PrometheusArgs, opts: ResourceOptions = None
    ):

        super().__init__("prismxfi:prometheus", name, {}, opts)

        # create a task execution IAM role
        # Create an IAM role that can be used by our service's task.
        role = aws.iam.Role(
            f"{name}-exec-role",
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

        rpa = aws.iam.RolePolicyAttachment(
            f"{name}-task-policy",
            role=role.name,
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

        service_dicovery_policy = aws.iam.Policy("ECSServiceDiscoveryInlinePolicy",
                        description="describe and list services, tasks, containers, and EC2 instances",
                        policy=json.dumps({
                            "Version": "2012-10-17",
                            "Statement": [{
                                "Action": ["ecs:DescribeTasks",
                                        "ECS:ListClusters",
                                        "ECS:ListTasks",
                                        "ECS:DescribeClusters",
                                        "ECS:DescribeTasks",
                                        "ECS:DescribeTaskDefinition",
                                        "ECS:ListServices",
                                        "ECS:DescribeServices",
                                ],
                                "Effect": "Allow",
                                "Resource": "*",
                            }]
                        }))
        service_dicovery_policy_attachment = aws.iam.RolePolicyAttachment("app-access-policy",
                                                              role=app_task_role.name,
                                                              policy_arn=service_dicovery_policy
                                                              )

        # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html
        container_name = f"{name}-prometheus-grafana-container"
        self.task_definition = aws.ecs.TaskDefinition(
            f"{name}-app-task",
            cpu="1024",
            memory="1024",
            execution_role_arn=role.arn,
            task_role_arn=app_task_role.arn,
            network_mode="awsvpc",
            family="Prometheus-Grafana",
            container_definitions=json.dumps([
                    # sidecar container, which periodically updates prom scrape targets in /tmp/ecs_auto_sd.yaml
                    # might be needed because if there are multiple instances in cloud map will the DNS query return 1 instance or
                    # all? The Boto3 ecs auto-discovery container will periodically scan the ecs task IP addresses and auto-generate 
                    # the sd_file_config containing the Prometheus scrape targets that the Prometheus.yaml file will use.
                    {
                        "name": "ecs-sd",
                        "image": "<ecs_sd_image_from_ecr>",
                        "memory": 512,
                        "cpu": 256,
                        "essential": True
                    },
                    {
                        "name": "grafana",
                        "image": "grafana/grafana:latest",
                        "memory": 512,
                        "cpu": 256,
                        "essential": True,
                        "portMappings": [{"containerPort": 3000, "protocol": "tcp"}],
                    },
                    {
                        "name": "prometheus-server",
                        # this is the prometheus docker file with prometheus.yaml 
                        # added to a directory. The directory is specified
                        # in the VOLUME directive - create as root USER - of the Dockerfile, which matches the containerPath
                        # in this task-definition.
                        "image": "968467591626.dkr.ecr.us-west-2.amazonaws.com/prometheus:latest", 
                        "user": "root",
                        "memory": 512,
                        "cpu": 512,
                        "essential": True,
                        "portMappings": [{"containerPort": 9090, "protocol": "tcp"}],
                        "command":[
                            "--storage.tsdb.retention.time=15d",
                            "--config.file=/etc/config/prometheus.yaml",
                            "--storage.tsdb.path=/data",
                            "--web.console.libraries=/etc/prometheus/console_libraries",
                            "--web.console.templates=/etc/prometheus/consoles",
                            "--web.enable-lifecycle"
                        ],
                        "logConfiguration": {
                            "logDriver": "awslogs",
                            "options": {
                                "awslogs-group": "/ecs/Prometheus",
                                "awslogs-region": aws.get_region().name,
                                "awslogs-stream-prefix": "server",
                                "awslogs-create-group": "true"
                            },
                        },
                        "mountPoints":[{
                            "sourceVolume":"configVolume",
                            "containerPath":"/etc/config",
                            "readOnly":False
                            },
                            {
                            "sourceVolume":"logsVolume",
                            "containerPath":"/data"
                            }
                        ],
                        "dependsOn": [ # wait for ecs auto-discovery container
                            {
                                "containerName": "ecs-sd",
                                "condition": "START"
                            }
                        ]
                    },       
                ]),
            volumes=[aws.ecs.TaskDefinitionVolumeArgs(
                name="configVolume",
            )],
            requires_compatibilities=["FARGATE"],
            opts=ResourceOptions(parent=self),
        )

        self.service = aws.ecs.Service(
            f"{name}-prom-grafana",
            # ECS cluster would be shared among many resources/services so it should be passed in to the constructor
            cluster=args.ecs_cluster_arn,
            desired_count=1,
            launch_type="FARGATE",
            task_definition=self.task_definition.arn,
            network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(
                subnets=args.subnet_ids,
                security_groups=args.sg_group,
            ),
                                                    
            opts=ResourceOptions(parent=self),

        )

        self.register_outputs({})