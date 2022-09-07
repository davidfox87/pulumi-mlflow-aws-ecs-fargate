"""An AWS Python Pulumi program"""
from pulumi import export, Config, StackReference, Output
from pulumi_aws import iam, eks
import json

# Get config data
config = Config()
service_name = config.get('service_name') or 'mlops'


# reference the networking stack
networkingStack = StackReference(config.require('NetworkingStack'))

eks_role = iam.Role(
    'eks-iam-role',
    assume_role_policy=json.dumps({
        'Version': '2012-10-17',
        'Statement': [
            {
                'Action': 'sts:AssumeRole',
                'Principal': {
                    'Service': 'eks.amazonaws.com'
                },
                'Effect': 'Allow',
                'Sid': ''
            }
        ],
    }),
)

iam.RolePolicyAttachment(
    'eks-service-policy-attachment',
    role=eks_role.id,
    policy_arn='arn:aws:iam::aws:policy/AmazonEKSServicePolicy',
)


iam.RolePolicyAttachment(
    'eks-cluster-policy-attachment',
    role=eks_role.id,
    policy_arn='arn:aws:iam::aws:policy/AmazonEKSClusterPolicy',
)

## Ec2 NodeGroup Role

ec2_role = iam.Role(
    'ec2-nodegroup-iam-role',
    assume_role_policy=json.dumps({
        'Version': '2012-10-17',
        'Statement': [
            {
                'Action': 'sts:AssumeRole',
                'Principal': {
                    'Service': 'ec2.amazonaws.com'
                },
                'Effect': 'Allow',
                'Sid': ''
            }
        ],
    }),
)

iam.RolePolicyAttachment(
    'eks-workernode-policy-attachment',
    role=ec2_role.id,
    policy_arn='arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy',
)


iam.RolePolicyAttachment(
    'eks-cni-policy-attachment',
    role=ec2_role.id,
    policy_arn='arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy',
)

iam.RolePolicyAttachment(
    'ec2-container-ro-policy-attachment',
    role=ec2_role.id,
    policy_arn='arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly',
)


cluster = eks.Cluster('my-cluster',
    vpc_config=eks.ClusterVpcConfigArgs(
        vpc_id = networkingStack.get_output("vpc_id"),
        subnet_ids=[networkingStack.get_output("public_subnet1"),
                    networkingStack.get_output("public_subnet2"),
        ],
        security_group_ids=[networkingStack.get_output("eks_security_group")],
        public_access_cidrs=['0.0.0.0/0'],
    ),
    role_arn=eks_role.arn,
    tags={
        'Name': 'pulumi-eks-cluster',
    },
)


eks_node_group = eks.NodeGroup(
    'eks-node-group',
    cluster_name=cluster.name, # cluster Node group will attach to 
    node_group_name='pulumi-eks-nodegroup',
    node_role_arn=ec2_role.arn,
    instance_types=["t3.medium"], # this is the default
    subnet_ids=[networkingStack.get_output("public_subnet1"),
                networkingStack.get_output("public_subnet2"),
    ],
    tags={
        'Name': 'pulumi-cluster-nodeGroup',
    },
    scaling_config=eks.NodeGroupScalingConfigArgs(
        desired_size=2,
        max_size=2,
        min_size=1,
    ),
)
# Export the cluster's kubeconfig.
export('kubeconfig', cluster.kubeconfig)