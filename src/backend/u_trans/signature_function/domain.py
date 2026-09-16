import abc
from dataclasses import dataclass
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
    status: TransactionStatus

@dataclass
class DomainEvent:
    event_type: str
    transaction_id: str
    user_id: str

class CryptographicPort(abc.ABC):
    @abc.abstractmethod
    def verify(self, public_key_pem: str, signature_b64: str, payload_hash: str) -> bool:
        pass

class DeviceKeyRepositoryPort(abc.ABC):
    @abc.abstractmethod
    def get_public_key(self, user_id: str, device_id: str) -> str:
        pass

class TransactionRepositoryPort(abc.ABC):
    @abc.abstractmethod
    def get_transaction(self, user_id: str, transaction_id: str) -> Transaction:
        pass
        
    @abc.abstractmethod
    def update_status(self, user_id: str, transaction_id: str, status: TransactionStatus) -> None:
        pass

class EventPublisherPort(abc.ABC):
    @abc.abstractmethod
    def publish(self, event: DomainEvent) -> None:
        pass

class VerifySignatureUseCase:
    def __init__(
        self,
        crypto_port: CryptographicPort,
        key_repo: DeviceKeyRepositoryPort,
        tx_repo: TransactionRepositoryPort,
        event_pub: EventPublisherPort
    ):
        self.crypto_port = crypto_port
        self.key_repo = key_repo
        self.tx_repo = tx_repo
        self.event_pub = event_pub

    def verify_and_approve(
        self,
        user_id: str,
        device_id: str,
        transaction_id: str,
        signature_b64: str,
        payload_hash: str
    ) -> Transaction:
        
        # 1. Recuperar transaccion y validar estado
        tx = self.tx_repo.get_transaction(user_id, transaction_id)
        if not tx:
            raise ValueError("Transaction not found")
            
        if tx.status != TransactionStatus.PENDING_APPROVAL:
            raise ValueError(f"Transaction is in invalid state: {tx.status.value}")

        # 2. Recuperar llave publica del Enclave (registrada en B-01)
        public_key = self.key_repo.get_public_key(user_id, device_id)
        if not public_key:
            raise ValueError("Device/Key not found for this user")

        # 3. Validacion criptografica asimetrica
        is_valid = self.crypto_port.verify(public_key, signature_b64, payload_hash)
        if not is_valid:
            raise ValueError("Cryptographic signature is invalid")

        # 4. Actualizar estado y publicar evento
        self.tx_repo.update_status(user_id, transaction_id, TransactionStatus.APPROVED)
        tx.status = TransactionStatus.APPROVED
        
        event = DomainEvent(
            event_type="TransferApproved",
            transaction_id=transaction_id,
            user_id=user_id
        )
        self.event_pub.publish(event)
        
        return tx
