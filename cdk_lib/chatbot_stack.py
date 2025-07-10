import os
from aws_cdk import Stack, RemovalPolicy

from aws_cdk.aws_s3 import Bucket
from aws_cdk.aws_dynamodb import Table, Attribute, AttributeType, BillingMode
from aws_cdk.aws_ec2 import Vpc
from aws_cdk.aws_ecs import Cluster, ContainerImage
from aws_cdk.aws_ecs_patterns import (
    ApplicationLoadBalancedFargateService,
    ApplicationLoadBalancedTaskImageOptions,
)


class ChatbotStack(Stack):
    customer: str

    def __init__(self, scope, id, customer: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.customer = customer
        print(f"Creating chatbot stack for {customer}")
        # Create resources here

        # Create an S3 bucket
        bucket = Bucket(
            self,
            self.build_name("chatbot-bucket"),
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Create a DynamoDB table
        user_management_table = Table(
            self,
            self.build_name("user-management-table"),
            partition_key=Attribute(name="PK", type=AttributeType.STRING),
            sort_key=Attribute(name="SK", type=AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=BillingMode.PAY_PER_REQUEST,
        )

        # VPC with default settings (1 NAT Gateway)
        vpc = Vpc(self, self.build_name("StreamlitVpc"), max_azs=2)

        # ECS Cluster
        cluster = Cluster(self, self.build_name("StreamlitCluster"), vpc=vpc)

        # Fargate service with load balancer using local Dockerfile
        service = ApplicationLoadBalancedFargateService(
            self,
            self.build_name("StreamlitFargateService"),
            cluster=cluster,
            cpu=512,
            memory_limit_mib=1024,
            desired_count=1,
            public_load_balancer=True,
            task_image_options=ApplicationLoadBalancedTaskImageOptions(
                image=ContainerImage.from_asset("."),
                container_port=6969,
                environment={
                    "BUCKET_NAME": bucket.bucket_name,
                    "USER_TABLE_NAME": user_management_table.table_name,
                    "CUSTOMER": self.customer,
                },
            ),
        )

    def build_name(self, name: str) -> str:
        return f"{self.customer}-{name}"
