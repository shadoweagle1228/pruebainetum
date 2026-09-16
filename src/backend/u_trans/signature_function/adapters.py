import boto3
import json
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from domain import (
    CryptographicPort, DeviceKeyRepositoryPort, TransactionRepositoryPort,
    EventPublisherPort, Transaction, TransactionStatus, DomainEvent
)

class RSACryptographicAdapter(CryptographicPort):
    def verify(self, public_key_pem: str, signature_b64: str, payload_hash: str) -> bool:
        try:
            public_key = load_pem_public_key(public_key_pem.encode('utf-8'))
            signature = base64.b64decode(signature_b64)
            # The payload hash must be verified. We assume the mobile sent the SHA256 string
            # In a real scenario we sign the raw bytes, but here we sign the utf8 representation
            # of the hash for simplicity.
            public_key.verify(
                signature,
                payload_hash.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

class DynamoDBAdapter(DeviceKeyRepositoryPort, TransactionRepositoryPort):
    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def get_public_key(self, user_id: str, device_id: str) -> str:
        response = self.table.get_item(
            Key={'PK': f"USER#{user_id}", 'SK': f"DEVICE#{device_id}"}
        )
        item = response.get('Item')
        if item and item.get('Status') == 'ACTIVE':
            return item.get('PublicKeyPEM')
        return None

    def get_transaction(self, user_id: str, transaction_id: str) -> Transaction:
        response = self.table.get_item(
            Key={'PK': f"USER#{user_id}", 'SK': f"TX#{transaction_id}"}
        )
        item = response.get('Item')
        if not item:
            return None
        return Transaction(
            transaction_id=transaction_id,
            initiator_user_id=user_id,
            status=TransactionStatus(item.get('Status'))
        )

    def update_status(self, user_id: str, transaction_id: str, status: TransactionStatus) -> None:
        self.table.update_item(
            Key={'PK': f"USER#{user_id}", 'SK': f"TX#{transaction_id}"},
            UpdateExpression="SET #s = :status",
            ExpressionAttributeNames={"#s": "Status"},
            ExpressionAttributeValues={":status": status.value}
        )

class EventBridgeAdapter(EventPublisherPort):
    def __init__(self, bus_name: str):
        self.bus_name = bus_name
        self.client = boto3.client('events')

    def publish(self, event: DomainEvent) -> None:
        self.client.put_events(
            Entries=[
                {
                    'Source': 'com.bank.utrans',
                    'DetailType': event.event_type,
                    'Detail': json.dumps({
                        "transactionId": event.transaction_id,
                        "userId": event.user_id
                    }),
                    'EventBusName': self.bus_name
                }
            ]
        )
