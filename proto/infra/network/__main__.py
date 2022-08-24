import json

import pulumi_aws as aws
from pulumi import Config, export

from network import Vpc, VpcArgs

config = Config()

my_network = Vpc(f'MLOps-VPC', VpcArgs())

# export networking stack variables
export("vpc_id", my_network.vpc.id)
export("public_subnet1", my_network.subnets[0].id)
export("public_subnet2", my_network.subnets[1].id)
export("alb_sg_id", my_network.internet_facing_lb_sg.id)
export("rds_sg_id", my_network.rds_sg.id)
export("ecs_sg_id", my_network.ecs_sg.id)