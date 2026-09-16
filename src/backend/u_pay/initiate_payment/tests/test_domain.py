import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from decimal import Decimal

# Setup paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.modules['boto3'] = MagicMock()

from domain import InitiatePaymentUseCase, MessageQueuePort, PaymentRepositoryPort, BillPaymentStatus
import app

class TestPayDomain(unittest.TestCase):
    def setUp(self):
        self.queue = MagicMock(spec=MessageQueuePort)
        self.repo = MagicMock(spec=PaymentRepositoryPort)
        self.use_case = InitiatePaymentUseCase(self.queue, self.repo)

    def test_initiate_success(self):
        payment = self.use_case.initiate("U-1", "BILLER-1", "ACC-1", Decimal("100.50"))
        
        self.assertEqual(payment.status, BillPaymentStatus.QUEUED)
        self.assertEqual(payment.amount, Decimal("100.50"))
        
        self.repo.save.assert_called_once_with(payment)
        self.queue.enqueue_payment_command.assert_called_once_with(payment)

    def test_initiate_invalid_amount(self):
        with self.assertRaisesRegex(ValueError, "Amount must be greater than zero"):
            self.use_case.initiate("U-1", "BILLER-1", "ACC-1", Decimal("-10.00"))

class TestPayApp(unittest.TestCase):
    @patch('app.use_case')
    def test_handler_success(self, mock_use_case):
        mock_payment = MagicMock()
        mock_payment.payment_id = "PAY-001"
        mock_payment.status.value = "QUEUED"
        mock_use_case.initiate.return_value = mock_payment

        event = {
            "requestContext": {"authorizer": {"userId": "U-123"}},
            "body": json.dumps({
                "billerId": "B1",
                "accountNumber": "A1",
                "amount": "100.50"
            })
        }
        
        resp = app.handler(event, None)
        self.assertEqual(resp['statusCode'], 202)
        body = json.loads(resp['body'])
        self.assertEqual(body['paymentId'], "PAY-001")

if __name__ == '__main__':
    unittest.main()
