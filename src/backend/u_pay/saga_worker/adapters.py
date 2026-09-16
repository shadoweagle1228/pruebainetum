import boto3
import requests
from decimal import Decimal
from domain import (
    PaymentRepositoryPort, CoreBankingPort, BillerPort, BillPayment, BillPaymentStatus
)

class DynamoDBPaymentRepositoryAdapter(PaymentRepositoryPort):
    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def get_payment(self, user_id: str, payment_id: str) -> BillPayment:
        response = self.table.get_item(
            Key={'PK': f"USER#{user_id}", 'SK': f"PAY#{payment_id}"}
        )
        item = response.get('Item')
        if not item:
            return None
        return BillPayment(
            payment_id=payment_id,
            user_id=user_id,
            biller_id=item.get('BillerId'),
            account_number=item.get('AccountNumber'),
            amount=Decimal(item.get('Amount')),
            status=BillPaymentStatus(item.get('Status'))
        )
        
    def update_status(self, user_id: str, payment_id: str, status: BillPaymentStatus) -> None:
        self.table.update_item(
            Key={'PK': f"USER#{user_id}", 'SK': f"PAY#{payment_id}"},
            UpdateExpression="SET #s = :status",
            ExpressionAttributeNames={"#s": "Status"},
            ExpressionAttributeValues={":status": status.value}
        )

class HTTPCoreBankingAdapter(CoreBankingPort):
    def __init__(self, api_url: str):
        self.api_url = api_url

    def debit(self, account_id: str, amount: Decimal) -> bool:
        try:
            res = requests.post(f"{self.api_url}/v1/core/debit", json={"account": account_id, "amount": str(amount)}, timeout=5)
            return res.status_code == 200
        except Exception:
            return False

    def credit(self, account_id: str, amount: Decimal) -> bool:
        try:
            res = requests.post(f"{self.api_url}/v1/core/credit", json={"account": account_id, "amount": str(amount)}, timeout=5)
            return res.status_code == 200
        except Exception:
            return False

class HTTPBillerAdapter(BillerPort):
    def __init__(self, api_url: str):
        self.api_url = api_url

    def pay(self, biller_id: str, account_id: str, amount: Decimal) -> bool:
        try:
            res = requests.post(f"{self.api_url}/v1/biller/{biller_id}/pay", json={"account": account_id, "amount": str(amount)}, timeout=5)
            return res.status_code == 200
        except Exception:
            return False
