import abc
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal

class BillPaymentStatus(str, Enum):
    QUEUED = "QUEUED"
    DEBITING = "DEBITING"
    PAYING = "PAYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    COMPENSATING = "COMPENSATING"

@dataclass
class BillPayment:
    payment_id: str
    user_id: str
    biller_id: str
    account_number: str
    amount: Decimal
    status: BillPaymentStatus

class PaymentRepositoryPort(abc.ABC):
    @abc.abstractmethod
    def get_payment(self, user_id: str, payment_id: str) -> BillPayment:
        pass
    
    @abc.abstractmethod
    def update_status(self, user_id: str, payment_id: str, status: BillPaymentStatus) -> None:
        pass

class CoreBankingPort(abc.ABC):
    @abc.abstractmethod
    def debit(self, account_id: str, amount: Decimal) -> bool:
        pass
        
    @abc.abstractmethod
    def credit(self, account_id: str, amount: Decimal) -> bool:
        pass

class BillerPort(abc.ABC):
    @abc.abstractmethod
    def pay(self, biller_id: str, account_id: str, amount: Decimal) -> bool:
        pass

class SagaOrchestratorUseCase:
    def __init__(
        self,
        repo: PaymentRepositoryPort,
        core: CoreBankingPort,
        biller: BillerPort
    ):
        self.repo = repo
        self.core = core
        self.biller = biller

    def execute_payment_saga(self, user_id: str, payment_id: str) -> None:
        payment = self.repo.get_payment(user_id, payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
            
        # Idempotency check: Ignore if it's already processed
        if payment.status in (BillPaymentStatus.COMPLETED, BillPaymentStatus.FAILED):
            return

        # --- STEP 1: Debit ---
        self.repo.update_status(user_id, payment_id, BillPaymentStatus.DEBITING)
        debit_ok = self.core.debit(payment.account_number, payment.amount)
        if not debit_ok:
            self.repo.update_status(user_id, payment_id, BillPaymentStatus.FAILED)
            return

        # --- STEP 2: Pay Biller ---
        self.repo.update_status(user_id, payment_id, BillPaymentStatus.PAYING)
        pay_ok = self.biller.pay(payment.biller_id, payment.account_number, payment.amount)
        if not pay_ok:
            # --- STEP 3: Compensate (Reversal) ---
            self.repo.update_status(user_id, payment_id, BillPaymentStatus.COMPENSATING)
            credit_ok = self.core.credit(payment.account_number, payment.amount)
            if not credit_ok:
                # In real life, send alert to DLQ/humans for manual intervention
                raise RuntimeError("Critical Failure: Compensation credit failed!")
                
            self.repo.update_status(user_id, payment_id, BillPaymentStatus.FAILED)
            return

        # --- STEP 4: Complete ---
        self.repo.update_status(user_id, payment_id, BillPaymentStatus.COMPLETED)
