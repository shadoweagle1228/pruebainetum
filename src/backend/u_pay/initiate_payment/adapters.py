import boto3
import json
from domain import MessageQueuePort, PaymentRepositoryPort, BillPayment

class DynamoDBPaymentRepositoryAdapter(PaymentRepositoryPort):
    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def save(self, payment: BillPayment) -> None:
        self.table.put_item(
            Item={
                'PK': f"USER#{payment.user_id}",
                'SK': f"PAY#{payment.payment_id}",
                'BillerId': payment.biller_id,
                'AccountNumber': payment.account_number,
                'Amount': str(payment.amount),
                'Status': payment.status.value,
                'Type': 'BillPayment'
            }
        )

class SQSPaymentQueueAdapter(MessageQueuePort):
    def __init__(self, queue_url: str):
        self.sqs = boto3.client('sqs')
        self.queue_url = queue_url

    def enqueue_payment_command(self, payment: BillPayment) -> None:
        message_body = {
            "paymentId": payment.payment_id,
            "userId": payment.user_id
        }
        self.sqs.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(message_body)
        )
