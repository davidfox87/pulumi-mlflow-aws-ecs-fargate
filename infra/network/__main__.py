import json

import pulumi_aws as aws
from pulumi import Config, export, Output

from network import Vpc, VpcArgs

config = Config()

my_network = Vpc(f'MLOps-VPC', VpcArgs())

alb = aws.lb.LoadBalancer('alb',
                            security_groups=[my_network.internet_facing_lb_sg],
                            subnets=my_network.subnets
)

# export networking stack variables
export("vpc_id", my_network.vpc.id)
export("public_subnet1", my_network.subnets[0].id)
export("public_subnet2", my_network.subnets[1].id)
export("alb_sg_id", my_network.internet_facing_lb_sg.id)
export("rds_sg_id", my_network.rds_sg.id)
export("ecs_sg_id", my_network.ecs_sg.id)
export("postgres_public_sg", my_network.postgres_public_sg.id)
export("web_server_ecs_internal_sg", my_network.web_server_ecs_internal_sg.id)
export('alb_arn', alb.arn)


web_url=Output.concat('http://', alb.dns_name)
export('Web Service URL', web_url)