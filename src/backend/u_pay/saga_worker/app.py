import os
import json
import logging
from domain import SagaOrchestratorUseCase
from adapters import (
    DynamoDBPaymentRepositoryAdapter, HTTPCoreBankingAdapter, HTTPBillerAdapter
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = os.environ.get('CORE_TABLE_NAME')
CORE_API_URL = os.environ.get('CORE_API_URL', 'https://mock-core.internal')
BILLER_API_URL = os.environ.get('BILLER_API_URL', 'https://mock-biller.internal')

repo = DynamoDBPaymentRepositoryAdapter(table_name=TABLE_NAME)
core = HTTPCoreBankingAdapter(api_url=CORE_API_URL)
biller = HTTPBillerAdapter(api_url=BILLER_API_URL)

use_case = SagaOrchestratorUseCase(repo=repo, core=core, biller=biller)

def handler(event, context):
    """
    SQS Event Handler for batch processing.
    """
    for record in event.get('Records', []):
        try:
            body = json.loads(record.get('body', '{}'))
            payment_id = body.get('paymentId')
            user_id = body.get('userId')
            
            if not payment_id or not user_id:
                logger.warning("Message missing required fields. Dropping.")
                continue
                
            logger.info(f"Executing saga for Payment ID: {payment_id}")
            
            use_case.execute_payment_saga(user_id=user_id, payment_id=payment_id)
            
        except ValueError as ve:
            logger.error(f"Validation error for record: {str(ve)}")
        except Exception as e:
            logger.error(f"Unhandled error processing record: {str(e)}")
            # Raise exception to trigger SQS retry mechanism / DLQ
            raise e
