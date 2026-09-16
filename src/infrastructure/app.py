#!/usr/bin/env python3
import os
import aws_cdk as cdk
from stacks.iam_stack import IamStack

from stacks.trans_stack import TransStack

app = cdk.App()

env = cdk.Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region=os.getenv('CDK_DEFAULT_REGION')
)

iam_stack = IamStack(app, "IamStack", env=env)

# Pass the CoreTable reference to the U-TRANS stack
TransStack(app, "TransStack", core_table=iam_stack.core_table, env=env)

app.synth()
