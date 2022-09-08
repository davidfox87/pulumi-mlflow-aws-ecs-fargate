"""An AWS Python Pulumi program"""
from pulumi import export, Config, StackReference, Output, ResourceOptions
from pulumi_aws import iam
import pulumi_eks as eks
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
instance_profile_1 = iam.InstanceProfile('my-instance-profile1',
    iam.InstanceProfileArgs(role=eks_role))


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

instance_profile_2 = iam.InstanceProfile('my-instance-profile2',
    iam.InstanceProfileArgs(role=ec2_role))

cluster = eks.Cluster('my-cluster',
    eks.ClusterArgs(
        vpc_id=networkingStack.get_output("vpc_id"),
        subnet_ids=[networkingStack.get_output("public_subnet1"),
                    networkingStack.get_output("public_subnet2"),

        ],
        instance_roles=[eks_role, ec2_role],
        public_access_cidrs=['0.0.0.0/0'],
        skip_default_node_group = True
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

# Export the cluster's kubeconfig.
export('kubeconfig', cluster.kubeconfig)

