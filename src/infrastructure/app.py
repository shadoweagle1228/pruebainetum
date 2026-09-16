#!/usr/bin/env python3
import os
import aws_cdk as cdk
from stacks.iam_stack import IamStack

app = cdk.App()

# Define the environment (Account and Region can be set via env vars or CLI)
env = cdk.Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region=os.getenv('CDK_DEFAULT_REGION')
)

# Instantiate the U-IAM Stack (Bolt B-01)
IamStack(app, "IamStack", env=env)

app.synth()
