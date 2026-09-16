import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.modules['boto3'] = MagicMock()
sys.modules['cryptography.hazmat.primitives'] = MagicMock()
sys.modules['cryptography.hazmat.primitives.asymmetric'] = MagicMock()
sys.modules['cryptography.hazmat.primitives.serialization'] = MagicMock()

from domain import (
    VerifySignatureUseCase, CryptographicPort, DeviceKeyRepositoryPort,
    TransactionRepositoryPort, EventPublisherPort, Transaction, TransactionStatus
)
import app

class TestSignatureDomain(unittest.TestCase):
    def setUp(self):
        self.crypto = MagicMock(spec=CryptographicPort)
        self.keys = MagicMock(spec=DeviceKeyRepositoryPort)
        self.txs = MagicMock(spec=TransactionRepositoryPort)
        self.events = MagicMock(spec=EventPublisherPort)
        self.use_case = VerifySignatureUseCase(self.crypto, self.keys, self.txs, self.events)

    def test_verify_success(self):
        # Arrange
        tx = Transaction("TX-1", "U-1", TransactionStatus.PENDING_APPROVAL)
        self.txs.get_transaction.return_value = tx
        self.keys.get_public_key.return_value = "PEM-DATA"
        self.crypto.verify.return_value = True

        # Act
        result = self.use_case.verify_and_approve("U-1", "DEV-1", "TX-1", "sig", "hash")

        # Assert
        self.assertEqual(result.status, TransactionStatus.APPROVED)
        self.txs.update_status.assert_called_with("U-1", "TX-1", TransactionStatus.APPROVED)
        self.events.publish.assert_called_once()

    def test_verify_invalid_state(self):
        tx = Transaction("TX-1", "U-1", TransactionStatus.COMPLETED)
        self.txs.get_transaction.return_value = tx
        
        with self.assertRaisesRegex(ValueError, "invalid state"):
            self.use_case.verify_and_approve("U-1", "DEV-1", "TX-1", "sig", "hash")

    def test_verify_bad_signature(self):
        tx = Transaction("TX-1", "U-1", TransactionStatus.PENDING_APPROVAL)
        self.txs.get_transaction.return_value = tx
        self.keys.get_public_key.return_value = "PEM-DATA"
        self.crypto.verify.return_value = False
        
        with self.assertRaisesRegex(ValueError, "Cryptographic signature is invalid"):
            self.use_case.verify_and_approve("U-1", "DEV-1", "TX-1", "sig", "hash")

class TestSignatureApp(unittest.TestCase):
    @patch('app.use_case')
    def test_handler_success(self, mock_use_case):
        mock_tx = MagicMock()
        mock_tx.transaction_id = "TX-001"
        mock_tx.status.value = "APPROVED"
        mock_use_case.verify_and_approve.return_value = mock_tx

        event = {
            "requestContext": {"authorizer": {"userId": "U-123"}},
            "pathParameters": {"transactionId": "TX-001"},
            "body": json.dumps({
                "deviceId": "D1",
                "signatureBase64": "sig",
                "payloadHash": "hash"
            })
        }
        
        resp = app.handler(event, None)
        self.assertEqual(resp['statusCode'], 200)
        body = json.loads(resp['body'])
        self.assertEqual(body['status'], "APPROVED")

if __name__ == '__main__':
    unittest.main()
