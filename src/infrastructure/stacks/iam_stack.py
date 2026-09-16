import os
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_secretsmanager as secretsmanager,
    aws_kms as kms,
    aws_iam as iam,
)
from constructs import Construct

class IamStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. DynamoDB: Single Table Design for the whole system
        self.core_table = dynamodb.Table(
            self, "CoreTable",
            partition_key=dynamodb.Attribute(name="PK", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="SK", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY # For dev only, change to RETAIN for prod
        )

        # 2. KMS Key: Asymmetric key for JWT Signing (D13)
        jwt_key = kms.Key(
            self, "JwtAsymmetricKey",
            key_spec=kms.KeySpec.RSA_2048,
            key_usage=kms.KeyUsage.SIGN_VERIFY,
            description="Asymmetric KMS Key for signing JWTs in U-IAM",
            removal_policy=RemovalPolicy.DESTROY
        )

        # 3. Secrets Manager: Legacy API Key
        # In a real setup, you don't generate this here, you import an existing one.
        # Creating a placeholder for the CDK deployment.
        legacy_api_secret = secretsmanager.Secret(
            self, "LegacyApiSecret",
            description="API Key for Legacy Core Banking System",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"API_KEY": ""}',
                generate_string_key="API_KEY"
            )
        )

        # 4. Lambda Function: AuthFunction (B-01)
        auth_function = _lambda.Function(
            self, "AuthFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="app.handler",
            code=_lambda.Code.from_asset("../backend/u_iam/auth_function"),
            timeout=Duration.seconds(10),
            memory_size=512,
            environment={
                "CORE_TABLE_NAME": self.core_table.table_name,
                "LEGACY_API_URL": "https://api.legacy-bank.internal", # Should come from context/config
                "LEGACY_SECRET_ID": legacy_api_secret.secret_name,
                "KMS_KEY_ID": jwt_key.key_id
            }
        )

        # Apply Provisioned Concurrency for NFR-01 (Low Latency)
        version = auth_function.current_version
        alias = _lambda.Alias(
            self, "AuthFunctionLiveAlias",
            alias_name="live",
            version=version,
            provisioned_concurrent_executions=5
        )

        # Permissions
        self.core_table.grant_read_write_data(auth_function)
        legacy_api_secret.grant_read(auth_function)
        
        # Grant KMS sign permission (Action: kms:Sign)
        auth_function.add_to_role_policy(iam.PolicyStatement(
            actions=["kms:Sign"],
            resources=[jwt_key.key_arn]
        ))

        # 5. API Gateway (REST API)
        api = apigw.RestApi(
            self, "BankingApiGateway",
            rest_api_name="MobileBankingAPI",
            description="Single entrypoint for the Mobile App (Pure Serverless)"
        )

        # Route: POST /api/v1/auth/login
        api_v1 = api.root.add_resource("api").add_resource("v1")
        auth_resource = api_v1.add_resource("auth")
        login_resource = auth_resource.add_resource("login")
        
        login_integration = apigw.LambdaIntegration(
            alias, # Pointing to the provisioned concurrency alias
            proxy=True
        )
        login_resource.add_method("POST", login_integration)
