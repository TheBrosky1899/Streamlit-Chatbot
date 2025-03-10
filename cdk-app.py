import os
import aws_cdk as cdk
from cdk_lib.chatbot_stack import ChatbotStack

app = cdk.App()
customer = os.getenv("CUSTOMER", "customer")
ChatbotStack(
    app,
    f"{customer}-chatbot-stack",
    customer=customer,
    env=cdk.Environment(account=os.getenv("AWS_ACCOUNT"), region="us-east-1"),
)
