from pulumi import ComponentResource, ResourceOptions
from pulumi_aws import ec2, get_availability_zones, servicediscovery


class VpcArgs:
    """_summary_
    """
    def __init__(self,
                 cidr_block='10.100.0.0/16',
                 enable_dns_hostnames=True,
                 ):
        self.cidr_block = cidr_block
        self.enable_dns_hostnames = enable_dns_hostnames


class Vpc(ComponentResource):
    """ # provisions all network related stuff together
        # This includes:
        # 1) VPC
        # 2) public subnets (where internet-facing load balancer and bastion host will live)
        # 3) Internet gateway (and route table with associations)
        # 6) security groups (that can be used later)
    Args:
        ComponentResource (_type_): _description_
    """
    def __init__(self,
                 name: str,
                 args: VpcArgs,
                 opts: ResourceOptions = None):

        super().__init__('MLOps:network:VPC', name, {}, opts)

        vpc_name = f'{name}-vpc'
        self.vpc = ec2.Vpc(vpc_name,
                           cidr_block=args.cidr_block,
                           enable_dns_hostnames=args.enable_dns_hostnames,
                           tags={
                               'Name': vpc_name
                           },
                           opts=ResourceOptions(parent=self)
                           )

        # create internet gateway for public subnets
        igw_name = f'{name}-igw'
        self.igw = ec2.InternetGateway(igw_name,
                                       vpc_id=self.vpc.id,
                                       tags={
                                           'Name': igw_name
                                       },
                                       opts=ResourceOptions(parent=self)
                                       )

        rt_name = f'{name}-rt'
        self.route_table = ec2.RouteTable(rt_name,
                                          vpc_id=self.vpc.id,
                                          routes=[ec2.RouteTableRouteArgs(
                                              cidr_block='0.0.0.0/0',
                                              gateway_id=self.igw.id,
                                          )],
                                          tags={
                                              'Name': rt_name
                                          },
                                          opts=ResourceOptions(parent=self)
                                          )

        # Subnets, at least across two zones.
        all_zones = get_availability_zones()
        # limiting to 2 zones for speed and to meet minimal requirements.
        zone_names = [all_zones.names[0], all_zones.names[1]]
        self.subnets = []
        subnet_name_base = f'{name}-public-subnet'
        for zone in zone_names:
            vpc_subnet = ec2.Subnet(f'{subnet_name_base}-{zone}',
                                    assign_ipv6_address_on_creation=False,
                                    vpc_id=self.vpc.id,
                                    map_public_ip_on_launch=True,
                                    cidr_block=f'10.100.{len(self.subnets)}.0/24',
                                    availability_zone=zone,
                                    tags={
                                        'Name': f'{subnet_name_base}-{zone}',
                                    },
                                    opts=ResourceOptions(parent=self)
                                    )
                                    
            ec2.RouteTableAssociation(
                f'vpc-igw-route-table-assoc-{zone}',
                route_table_id=self.route_table.id,
                subnet_id=vpc_subnet.id,
                opts=ResourceOptions(parent=self)
            )
            self.subnets.append(vpc_subnet)


        app_security_group = ec2.SecurityGroup("security-group",
    
        vpc_id=self.vpc.id,
        description="Enables HTTP access",
        ingress=[ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=80,
            to_port=80,
            cidr_blocks=['0.0.0.0/0'],
        )],
        egress=[ec2.SecurityGroupEgressArgs(
            protocol='-1',
            from_port=0,
            to_port=0,
            cidr_blocks=['0.0.0.0/0'],
        )])

        internet_facing_lb_sg_name = f'{name}-internet-facing-lb-sg'
        self.internet_facing_lb_sg = ec2.SecurityGroup(internet_facing_lb_sg_name,
                                                          vpc_id=self.vpc.id,
                                                          tags={
                                                            'Name': internet_facing_lb_sg_name
                                                          },
                                                          description='Allow all inbound traffic on the load balancer listener ports',
                                                          ingress=[ec2.SecurityGroupIngressArgs(
                                                              protocol='tcp',
                                                              from_port=80,  # 80 for http
                                                              to_port=80,
                                                              cidr_blocks=[
                                                                  '0.0.0.0/0']
                                                            )],
                                                          egress=[ec2.SecurityGroupEgressArgs(
                                                              protocol='-1',
                                                              from_port=0,
                                                              to_port=0,
                                                              cidr_blocks=[
                                                                  '0.0.0.0/0'],
                                                          )],
                                                          opts=ResourceOptions(parent=self)
                                                          )

        mlflow_sg_name = f'{name}-extractor-ecs-sg'
        self.ecs_sg = ec2.SecurityGroup(
            mlflow_sg_name,
            vpc_id=self.vpc.id,
            description='receive traffic on port 5000 from internet-facing load balancer',
            tags={'Name': 'ecs-mlflow'},
            ingress=[
                ec2.SecurityGroupIngressArgs(
                    protocol='tcp',
                    from_port=5000,
                    to_port=5000,
                    # allow the load balancer to send traffic to this ECS service on port 5000
                    security_groups=[self.internet_facing_lb_sg.id]),
            ],
            egress=[ec2.SecurityGroupEgressArgs(
                protocol='-1',
                from_port=0,
                to_port=0,
                cidr_blocks=['0.0.0.0/0'],
            )],
            opts=ResourceOptions(parent=self)
        )


        # security group that allows ecs to access the rds
        rds_sg_name = f'{name}-rds-sg'
        self.rds_sg = ec2.SecurityGroup(rds_sg_name,
                                        vpc_id=self.vpc.id,
                                        description='Allow client access.',
                                        tags={
                                            'Name': rds_sg_name
                                        },
                                        ingress=[
                                            ec2.SecurityGroupIngressArgs(
                                                cidr_blocks=[
                                                    '0.0.0.0/0'], #limit to MLFlow ECS
                                                from_port=3306,
                                                to_port=3306,
                                                protocol='tcp',
                                                description='Allow rds access.'
                                            ),
                                        ],
                                        egress=[
                                            ec2.SecurityGroupEgressArgs(
                                                protocol='-1',
                                                from_port=0,
                                                to_port=0,
                                                cidr_blocks=[
                                                    '0.0.0.0/0'],
                                            )],
                                        opts=ResourceOptions(
                                            parent=self)
                                        )
        self.register_outputs({})