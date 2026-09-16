import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from decimal import Decimal

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.modules['boto3'] = MagicMock()
sys.modules['requests'] = MagicMock()

from domain import (
    SagaOrchestratorUseCase, PaymentRepositoryPort, CoreBankingPort, BillerPort,
    BillPayment, BillPaymentStatus
)

class TestSagaDomain(unittest.TestCase):
    def setUp(self):
        self.repo = MagicMock(spec=PaymentRepositoryPort)
        self.core = MagicMock(spec=CoreBankingPort)
        self.biller = MagicMock(spec=BillerPort)
        self.use_case = SagaOrchestratorUseCase(self.repo, self.core, self.biller)
        
        self.mock_payment = BillPayment("PAY-1", "U-1", "B-1", "ACC-1", Decimal("100"), BillPaymentStatus.QUEUED)

    def test_saga_success(self):
        self.repo.get_payment.return_value = self.mock_payment
        self.core.debit.return_value = True
        self.biller.pay.return_value = True
        
        self.use_case.execute_payment_saga("U-1", "PAY-1")
        
        self.core.debit.assert_called_once()
        self.biller.pay.assert_called_once()
        self.repo.update_status.assert_called_with("U-1", "PAY-1", BillPaymentStatus.COMPLETED)

    def test_saga_debit_fails(self):
        self.repo.get_payment.return_value = self.mock_payment
        self.core.debit.return_value = False
        
        self.use_case.execute_payment_saga("U-1", "PAY-1")
        
        self.biller.pay.assert_not_called()
        self.repo.update_status.assert_called_with("U-1", "PAY-1", BillPaymentStatus.FAILED)

    def test_saga_compensation(self):
        self.repo.get_payment.return_value = self.mock_payment
        self.core.debit.return_value = True
        self.biller.pay.return_value = False
        self.core.credit.return_value = True
        
        self.use_case.execute_payment_saga("U-1", "PAY-1")
        
        self.core.credit.assert_called_once() # Verify reversal occurred
        self.repo.update_status.assert_called_with("U-1", "PAY-1", BillPaymentStatus.FAILED)

    def test_saga_idempotent(self):
        self.mock_payment.status = BillPaymentStatus.COMPLETED
        self.repo.get_payment.return_value = self.mock_payment
        
        self.use_case.execute_payment_saga("U-1", "PAY-1")
        
        self.core.debit.assert_not_called()
        self.biller.pay.assert_not_called()

if __name__ == '__main__':
    unittest.main()
