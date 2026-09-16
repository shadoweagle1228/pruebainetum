import os
import json
import logging
from decimal import Decimal
from domain import InitiatePaymentUseCase
from adapters import DynamoDBPaymentRepositoryAdapter, SQSPaymentQueueAdapter

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = os.environ.get('CORE_TABLE_NAME')
QUEUE_URL = os.environ.get('PAYMENT_QUEUE_URL')

repo_adapter = DynamoDBPaymentRepositoryAdapter(table_name=TABLE_NAME)
queue_adapter = SQSPaymentQueueAdapter(queue_url=QUEUE_URL)
use_case = InitiatePaymentUseCase(queue_port=queue_adapter, repo_port=repo_adapter)

def handler(event, context):
    try:
        authorizer_context = event.get('requestContext', {}).get('authorizer', {})
        user_id = authorizer_context.get('userId')
        
        if not user_id:
            body = json.loads(event.get('body', '{}'))
            user_id = body.get('userId')
            if not user_id:
                return {"statusCode": 403, "body": json.dumps({"message": "Forbidden"})}

        body = json.loads(event.get('body', '{}'))
        biller_id = body.get('billerId')
        account = body.get('accountNumber')
        amount_str = body.get('amount')

        if not all([biller_id, account, amount_str]):
            return {"statusCode": 400, "body": json.dumps({"message": "Missing fields"})}

        amount = Decimal(str(amount_str))

        payment = use_case.initiate(
            user_id=user_id,
            biller_id=biller_id,
            account_number=account,
            amount=amount
        )

        return {
            "statusCode": 202,
            "body": json.dumps({
                "paymentId": payment.payment_id,
                "status": payment.status.value,
                "message": "Pago recibido y encolado para procesamiento asíncrono."
            })
        }

    except ValueError as ve:
        return {"statusCode": 400, "body": json.dumps({"message": str(ve)})}
    except Exception as e:
        logger.error(f"Internal Error: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"message": "Internal Server Error"})}
