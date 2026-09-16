import abc
import uuid
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum

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

class MessageQueuePort(abc.ABC):
    @abc.abstractmethod
    def enqueue_payment_command(self, payment: BillPayment) -> None:
        pass

class PaymentRepositoryPort(abc.ABC):
    @abc.abstractmethod
    def save(self, payment: BillPayment) -> None:
        pass

class InitiatePaymentUseCase:
    def __init__(
        self,
        queue_port: MessageQueuePort,
        repo_port: PaymentRepositoryPort
    ):
        self.queue_port = queue_port
        self.repo_port = repo_port

    def initiate(
        self,
        user_id: str,
        biller_id: str,
        account_number: str,
        amount: Decimal
    ) -> BillPayment:
        
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")

        payment = BillPayment(
            payment_id=f"PAY-{uuid.uuid4()}",
            user_id=user_id,
            biller_id=biller_id,
            account_number=account_number,
            amount=amount,
            status=BillPaymentStatus.QUEUED
        )

        # Transactional outbox pattern behavior:
        # Save to DB first, then enqueue. (In real-world, we'd use DynamoDB streams or outbox pattern to guarantee delivery).
        self.repo_port.save(payment)
        self.queue_port.enqueue_payment_command(payment)
        
        return payment
