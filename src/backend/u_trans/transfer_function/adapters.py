import boto3
import requests
from decimal import Decimal
from domain import (
    InterbankValidatorPort, TransactionRepositoryPort, Transaction, TransactionStatus
)

class DynamoDBTransactionRepositoryAdapter(TransactionRepositoryPort):
    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def save(self, transaction: Transaction) -> None:
        # PII Data (destination_account, amount) will be KMS encrypted at rest
        # by the DynamoDB table's built-in encryption configured via CDK.
        self.table.put_item(
            Item={
                'PK': f"USER#{transaction.initiator_user_id}",
                'SK': f"TX#{transaction.transaction_id}",
                'Amount': str(transaction.amount),
                'DestinationAccount': transaction.destination_account,
                'DestinationBankId': transaction.destination_bank_id,
                'Status': transaction.status.value,
                'Type': 'Transaction'
            }
        )

class HTTPInterbankValidatorAdapter(InterbankValidatorPort):
    def __init__(self, api_url: str):
        self.api_url = api_url

    def validate_account(self, bank_id: str, account: str) -> bool:
        # NFR-04: Fail-Fast Strict Timeout (1.5s max to fulfill <200ms internally)
        # Note: 1.5s is an extreme upper bound for edge cases, standard should be <150ms.
        try:
            response = requests.get(
                f"{self.api_url}/v1/banks/{bank_id}/accounts/{account}",
                timeout=1.5
            )
            return response.status_code == 200
        except requests.exceptions.Timeout:
            # Circuit Breaker pattern hook: Log this explicitly and abort
            # Do NOT block the thread waiting.
            raise RuntimeError("Interbank validation timed out (Fail-Fast)")
        except requests.exceptions.RequestException:
            return False
