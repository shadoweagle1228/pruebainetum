import os
import json
import logging
from domain import VerifySignatureUseCase
from adapters import RSACryptographicAdapter, DynamoDBAdapter, EventBridgeAdapter

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = os.environ.get('CORE_TABLE_NAME')
EVENT_BUS_NAME = os.environ.get('EVENT_BUS_NAME', 'default')

db_adapter = DynamoDBAdapter(table_name=TABLE_NAME)
crypto_adapter = RSACryptographicAdapter()
event_adapter = EventBridgeAdapter(bus_name=EVENT_BUS_NAME)

use_case = VerifySignatureUseCase(
    crypto_port=crypto_adapter,
    key_repo=db_adapter,
    tx_repo=db_adapter,
    event_pub=event_adapter
)

def handler(event, context):
    try:
        authorizer_context = event.get('requestContext', {}).get('authorizer', {})
        user_id = authorizer_context.get('userId')
        
        if not user_id:
            # Fallback for local testing without real API GW Authorizer
            user_id = json.loads(event.get('body', '{}')).get('userId')
            if not user_id:
                return {"statusCode": 403, "body": json.dumps({"message": "Forbidden"})}

        transaction_id = event.get('pathParameters', {}).get('transactionId')
        if not transaction_id:
            return {"statusCode": 400, "body": json.dumps({"message": "Missing transactionId"})}

        body = json.loads(event.get('body', '{}'))
        device_id = body.get('deviceId')
        signature = body.get('signatureBase64')
        payload_hash = body.get('payloadHash')

        if not all([device_id, signature, payload_hash]):
            return {"statusCode": 400, "body": json.dumps({"message": "Missing fields"})}

        tx = use_case.verify_and_approve(
            user_id=user_id,
            device_id=device_id,
            transaction_id=transaction_id,
            signature_b64=signature,
            payload_hash=payload_hash
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "transactionId": tx.transaction_id,
                "status": tx.status.value,
                "message": "Firma validada matemáticamente. Transferencia encolada para ejecución."
            })
        }

    except ValueError as ve:
        logger.warning(f"Signature validation failed: {str(ve)}")
        return {"statusCode": 400, "body": json.dumps({"message": str(ve)})}
    except Exception as e:
        logger.error(f"Internal Error: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"message": "Internal Server Error"})}
