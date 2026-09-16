from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_sqs as sqs,
    aws_dynamodb as dynamodb,
    aws_lambda_event_sources as eventsources,
)
from constructs import Construct

class PayStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, core_table: dynamodb.ITable, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. SQS Queue for Async Payment Processing
        payment_queue = sqs.Queue(
            self, "PaymentCommandsQueue",
            queue_name="PaymentCommandsQueue",
            visibility_timeout=Duration.seconds(30), # Processing shouldn't take longer
            retention_period=Duration.days(4)
        )

        # 2. B-04: Payment Initiation Lambda
        initiate_function = _lambda.Function(
            self, "InitiatePaymentFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="app.handler",
            code=_lambda.Code.from_asset("../backend/u_pay/initiate_payment"),
            timeout=Duration.seconds(3), # Ultra-fast API
            memory_size=256,
            environment={
                "CORE_TABLE_NAME": core_table.table_name,
                "PAYMENT_QUEUE_URL": payment_queue.queue_url
            }
        )

        # 3. B-05: Saga Worker Lambda
        saga_worker = _lambda.Function(
            self, "SagaWorkerFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="app.handler",
            code=_lambda.Code.from_asset("../backend/u_pay/saga_worker"),
            timeout=Duration.seconds(10), # Connects to multiple APIs
            memory_size=256,
            environment={
                "CORE_TABLE_NAME": core_table.table_name,
                "CORE_API_URL": "https://api.mockbank.internal",
                "BILLER_API_URL": "https://api.mockbiller.internal"
            }
        )
        
        # Attach SQS to Saga Worker
        saga_worker.add_event_source(eventsources.SqsEventSource(payment_queue, batch_size=5))

        # Permissions
        core_table.grant_read_write_data(initiate_function)
        core_table.grant_read_write_data(saga_worker)
        payment_queue.grant_send_messages(initiate_function)
        payment_queue.grant_consume_messages(saga_worker)
