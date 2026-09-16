from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_events as events,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
)
from constructs import Construct

class TransStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, core_table: dynamodb.ITable, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. EventBus for Domain Events (TransferApproved)
        bus = events.EventBus(self, "BankingEventBus", event_bus_name="BankingEventBus")

        # 2. B-02: Transfer Initiation Lambda
        transfer_function = _lambda.Function(
            self, "TransferFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="app.handler",
            code=_lambda.Code.from_asset("../backend/u_trans/transfer_function"),
            timeout=Duration.seconds(5), # Strict fail-fast
            memory_size=512,
            environment={
                "CORE_TABLE_NAME": core_table.table_name,
                "INTERBANK_API_URL": "https://api.mockbank.internal"
            }
        )

        # Apply Provisioned Concurrency for NFR-01
        alias_trans = _lambda.Alias(
            self, "TransferLiveAlias",
            alias_name="live",
            version=transfer_function.current_version,
            provisioned_concurrent_executions=5
        )

        # 3. B-03: Signature Verification Lambda
        signature_function = _lambda.Function(
            self, "SignatureFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="app.handler",
            code=_lambda.Code.from_asset("../backend/u_trans/signature_function"),
            timeout=Duration.seconds(10),
            memory_size=1024, # Crypto operations need CPU
            environment={
                "CORE_TABLE_NAME": core_table.table_name,
                "EVENT_BUS_NAME": bus.event_bus_name
            }
        )

        # Permissions
        core_table.grant_read_write_data(transfer_function)
        core_table.grant_read_write_data(signature_function)
        bus.grant_put_events_to(signature_function)
