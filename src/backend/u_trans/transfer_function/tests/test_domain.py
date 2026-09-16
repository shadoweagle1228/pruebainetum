import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from decimal import Decimal

# Setup paths for tests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.modules['boto3'] = MagicMock()
sys.modules['requests'] = MagicMock()

import app
from domain import InitiateTransferUseCase, InterbankValidatorPort, TransactionRepositoryPort

class TestTransferDomain(unittest.TestCase):
    def setUp(self):
        self.validator = MagicMock(spec=InterbankValidatorPort)
        self.repo = MagicMock(spec=TransactionRepositoryPort)
        self.use_case = InitiateTransferUseCase(self.validator, self.repo)

    def test_initiate_success(self):
        self.validator.validate_account.return_value = True
        
        tx = self.use_case.initiate("U-1", Decimal("150.00"), "B-001", "ACC-123")
        
        self.assertEqual(tx.status.value, "PENDING_APPROVAL")
        self.repo.save.assert_called_once()
        self.validator.validate_account.assert_called_once_with("B-001", "ACC-123")

    def test_initiate_invalid_account(self):
        self.validator.validate_account.return_value = False
        
        with self.assertRaisesRegex(ValueError, "Invalid destination account"):
            self.use_case.initiate("U-1", Decimal("150.00"), "B-001", "ACC-123")
            
        self.repo.save.assert_not_called()

class TestTransferApp(unittest.TestCase):
    @patch('app.use_case')
    def test_handler_success(self, mock_use_case):
        mock_tx = MagicMock()
        mock_tx.transaction_id = "TX-001"
        mock_tx.status.value = "PENDING_APPROVAL"
        mock_use_case.initiate.return_value = mock_tx

        event = {
            "requestContext": {"authorizer": {"userId": "U-123"}},
            "body": json.dumps({
                "destinationBankId": "B1",
                "destinationAccount": "A1",
                "amount": "100.50"
            })
        }
        
        resp = app.handler(event, None)
        self.assertEqual(resp['statusCode'], 202)
        body = json.loads(resp['body'])
        self.assertEqual(body['transactionId'], "TX-001")

if __name__ == '__main__':
    unittest.main()
