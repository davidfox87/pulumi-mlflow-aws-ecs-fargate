"""An AWS Python Pulumi program"""

import pulumi_aws as aws
import pulumi_docker as docker
import json

repo = aws.ecr.Repository("churn-train")

ecr_creds = aws.ecr.get_authorization_token()

lambda_image = docker.Image("test_lambda",
    image_name=repo.repository_url,
    build="./steps",
    skip_push=False,
    registry=docker.ImageRegistry(server=repo.repository_url, username=ecr_creds.user_name, password=ecr_creds.password)
)

iam_role_lambda = aws.iam.Role(
            "exec-role",
            assume_role_policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                            {
                            "Effect": "Allow",
                            "Principal": { "Service": "lambda.amazonaws.com"},
                            "Action": "sts:AssumeRole"
                            }
                        ]
                    }
            ),
            inline_policies=[aws.iam.RoleInlinePolicyArgs(name='s3-access',
                                                          policy='''{"Version":"2012-10-17",
                                                                "Statement":[
                                                                    {
                                                                        "Effect":"Allow",
                                                                        "Action":[
                                                                            "s3:GetObject"
                                                                        ],
                                                                        "Resource":[
                                                                            "arn:aws:s3:::churn-dataset",
                                                                            "arn:aws:s3:::churn-dataset/*"
                                                                        ]
                                                                    }
                                                                ]
                                                                }'''
                                                          )],
)

test_lambda = aws.lambda_.Function("testLambda",
                                    package_type="Image",
                                    role=iam_role_lambda.arn,
                                    image_uri=lambda_image.image_name,
                                    timeout=900
    )
