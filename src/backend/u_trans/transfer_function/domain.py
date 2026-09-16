import abc
import uuid
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

class TransactionStatus(str, Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

@dataclass
class Transaction:
    transaction_id: str
    initiator_user_id: str
    amount: Decimal
    destination_account: str
    destination_bank_id: str
    status: TransactionStatus

class InterbankValidatorPort(abc.ABC):
    @abc.abstractmethod
    def validate_account(self, bank_id: str, account: str) -> bool:
        pass

class TransactionRepositoryPort(abc.ABC):
    @abc.abstractmethod
    def save(self, transaction: Transaction) -> None:
        pass

class InitiateTransferUseCase:
    def __init__(
        self,
        validator_port: InterbankValidatorPort,
        repo_port: TransactionRepositoryPort
    ):
        self.validator_port = validator_port
        self.repo_port = repo_port

    def initiate(
        self,
        initiator_user_id: str,
        amount: Decimal,
        destination_bank_id: str,
        destination_account: str
    ) -> Transaction:
        
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")

        # Synchronous Fail-Fast Validation (SLA < 200ms)
        is_valid = self.validator_port.validate_account(destination_bank_id, destination_account)
        if not is_valid:
            raise ValueError("Invalid destination account")

        transaction = Transaction(
            transaction_id=f"TX-{uuid.uuid4()}",
            initiator_user_id=initiator_user_id,
            amount=amount,
            destination_account=destination_account,
            destination_bank_id=destination_bank_id,
            status=TransactionStatus.PENDING_APPROVAL
        )

        self.repo_port.save(transaction)
        return transaction
