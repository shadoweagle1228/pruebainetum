import os
import json
import logging
from decimal import Decimal
from domain import InitiateTransferUseCase
from adapters import DynamoDBTransactionRepositoryAdapter, HTTPInterbankValidatorAdapter

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = os.environ.get('CORE_TABLE_NAME')
INTERBANK_API_URL = os.environ.get('INTERBANK_API_URL', 'https://api.mockbank.internal')

validator = HTTPInterbankValidatorAdapter(api_url=INTERBANK_API_URL)
repo = DynamoDBTransactionRepositoryAdapter(table_name=TABLE_NAME)
use_case = InitiateTransferUseCase(validator_port=validator, repo_port=repo)

def handler(event, context):
    try:
        # Zero-Trust: Caller identity is extracted from the JWT Custom Authorizer context
        authorizer_context = event.get('requestContext', {}).get('authorizer', {})
        user_id = authorizer_context.get('userId')
        
        if not user_id:
            # If local testing without authorizer, fallback to body (NOT for prod)
            body = json.loads(event.get('body', '{}'))
            user_id = body.get('initiatorUserId')
            if not user_id:
                return {"statusCode": 403, "body": json.dumps({"message": "Forbidden"})}

        body = json.loads(event.get('body', '{}'))
        bank_id = body.get('destinationBankId')
        account = body.get('destinationAccount')
        amount_str = body.get('amount')

        if not all([bank_id, account, amount_str]):
            return {"statusCode": 400, "body": json.dumps({"message": "Missing fields"})}

        amount = Decimal(str(amount_str))

        transaction = use_case.initiate(
            initiator_user_id=user_id,
            amount=amount,
            destination_bank_id=bank_id,
            destination_account=account
        )

        return {
            "statusCode": 202,
            "body": json.dumps({
                "transactionId": transaction.transaction_id,
                "status": transaction.status.value,
                "message": "Validación interbancaria exitosa. Esperando firmas del Enclave."
            })
        }

    except ValueError as ve:
        return {"statusCode": 400, "body": json.dumps({"message": str(ve)})}
    except RuntimeError as re:
        # E.g., Fail-Fast timeout
        logger.error(f"Fail-Fast applied: {str(re)}")
        return {"statusCode": 503, "body": json.dumps({"message": "Service Unavailable"})}
    except Exception as e:
        logger.error(f"Internal Error: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"message": "Internal Server Error"})}
