import os
from aws_cdk import Stack, RemovalPolicy

from aws_cdk.aws_s3 import Bucket
from aws_cdk.aws_dynamodb import Table, Attribute, AttributeType, BillingMode
from aws_cdk.aws_ec2 import Vpc
from aws_cdk.aws_ecs import FargateTaskDefinition, ContainerImage, PortMapping, Protocol
from aws_cdk.aws_ecs_patterns import ApplicationLoadBalancedFargateService
from aws_cdk.aws_ecr_assets import Platform
from aws_cdk.aws_certificatemanager import Certificate
from aws_cdk.aws_elasticloadbalancingv2 import SslPolicy


class ChatbotStack(Stack):
    customer: str

    def __init__(self, scope, id, customer: str, **kwargs):
        super().__init__(scope, id, **kwargs)
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

        # Create a VPC
        vpc = Vpc(
            self,
            self.build_name("vpc"),
            max_azs=2,
        )

        # Create a Fargate task definition
        task_definition = FargateTaskDefinition(
            self,
            self.build_name("task-definition"),
            cpu=256,  # TODO: optimize?
            memory_limit_mib=512,
        )

        image = ContainerImage.from_asset(
            directory="",
            platform=Platform.LINUX_AMD64,
            build_args={"STAGE": "Nah"},  # TODO: stage?
        )

        container = task_definition.add_container(
            self.build_name("container"),
            image=image,
            interactive=True,
            pseudo_terminal=True,
            secrets={},
            environment={},
        )

        container.add_port_mappings(
            PortMapping(container_port=6969, protocol=Protocol.TCP)
        )

        # Create a certificate
        certificate = Certificate(
            self,
            self.build_name("certificate"),
            domain_name=f"{self.customer}.example.com",  # TODO: bring your own domain?
        )

        fargate_service = ApplicationLoadBalancedFargateService(
            self,
            self.build_name("fargate-service"),
            public_load_balancer=True,
            task_definition=task_definition,
            redirect_http=True,
            certificate=certificate,
            ssl_policy=SslPolicy.RECOMMENDED,
            vpc=vpc,
        )

    def build_name(self, name: str) -> str:
        return f"{self.customer}-{name}"
