"""An AWS Python Pulumi program"""
from venv import create
from pulumi import export, Config, StackReference, Output, ResourceOptions
from pulumi_aws import iam
import pulumi_eks as eks
import json

# Get config data
config = Config()
service_name = config.get('service_name') or 'mlops'


# reference the networking stack
networkingStack = StackReference(config.require('NetworkingStack'))

managed_policy_arns = ['arn:aws:iam::aws:policy/AmazonEKSServicePolicy',
                        'arn:aws:iam::aws:policy/AmazonEKSClusterPolicy'
]
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

for i, policy in enumerate(managed_policy_arns):
    rpa = iam.RolePolicyAttachment(
        f"eks-role-policy-{i}",
        role=eks_role.id,
        policy_arn=policy,
    )

instance_profile_1 = iam.InstanceProfile('my-instance-profile1',
    iam.InstanceProfileArgs(role=eks_role))


## Ec2 NodeGroup Role
managed_policy_arns = ['arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy',
                        'arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy',
                        'arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly'
]

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

for i, policy in enumerate(managed_policy_arns):
    rpa = iam.RolePolicyAttachment(
        f"ec2-role-policy-{i}",
        role=ec2_role.id,
        policy_arn=policy,
    )

instance_profile_2 = iam.InstanceProfile('my-instance-profile2',
    iam.InstanceProfileArgs(role=ec2_role))


cluster = eks.Cluster('my-cluster',
    eks.ClusterArgs(
        vpc_id=networkingStack.get_output("vpc_id"),
        # Mixed (recommended): Set both privateSubnetIds and publicSubnetIds
        # Default all worker nodes to run in private subnets, and use the public subnets for internet-facing load balancers.
        public_subnet_ids=[networkingStack.get_output("public_subnet1"),
                            networkingStack.get_output("public_subnet2"),
        ],
        # private_subnet_ids=[networkingStack.get_output("private_subnet1"),
        #             networkingStack.get_output("private_subnet2"),
        # ],
        #instance_role=ec2_role,
        service_role=eks_role,
        public_access_cidrs=['0.0.0.0/0'],
        #skip_default_node_group = True,
        #create_oidc_provider=True
    )
)


# First, create a node group for fixed compute.
fixed_node_group = eks.NodeGroup('my-cluster-ng1',
    cluster = cluster.core,
    instance_type = 't2.medium',
    desired_capacity = 2,
    min_size = 1,
    max_size = 3,
    labels = {'ondemand': 'true'},
    instance_profile = instance_profile_2,
    opts = ResourceOptions(
        parent = cluster,
        providers = {
            'kubernetes': cluster.provider,
        }
    )
)

# https://www.pulumi.com/docs/guides/crosswalk/aws/eks/




# Export the cluster's kubeconfig.
export('kubeconfig', cluster.kubeconfig)

