import abc
import datetime
from dataclasses import dataclass
from typing import Optional
from enum import Enum

# --- Value Objects & Enums ---
class DeviceStatus(str, Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"

@dataclass
class JWT:
    token: str
    expires_at: int

@dataclass
class LegacyCredentials:
    username: str
    password: str

# --- Entities ---
@dataclass
class User:
    user_id: str
    role: str
    status: str

@dataclass
class Device:
    device_id: str
    user_id: str
    push_token: str
    public_key_pem: str
    status: DeviceStatus
    created_at: int

    def revoke(self):
        self.status = DeviceStatus.REVOKED

# --- Ports (Outbound / Driven) ---
class LegacyAuthPort(abc.ABC):
    @abc.abstractmethod
    def authenticate(self, credentials: LegacyCredentials) -> Optional[User]:
        pass

class DeviceRepositoryPort(abc.ABC):
    @abc.abstractmethod
    def save(self, device: Device) -> None:
        pass

    @abc.abstractmethod
    def find_by_user_and_device(self, user_id: str, device_id: str) -> Optional[Device]:
        pass

class TokenGeneratorPort(abc.ABC):
    @abc.abstractmethod
    def generate_token(self, user: User, device: Device) -> JWT:
        pass

# --- Use Cases (Inbound / Driving) ---
class AuthenticationUseCase:
    def __init__(
        self,
        auth_port: LegacyAuthPort,
        device_repo: DeviceRepositoryPort,
        token_generator: TokenGeneratorPort
    ):
        self.auth_port = auth_port
        self.device_repo = device_repo
        self.token_generator = token_generator

    def login(
        self, 
        credentials: LegacyCredentials, 
        device_id: str, 
        push_token: str, 
        public_key_pem: str
    ) -> JWT:
        # 1. Authenticate with Legacy System
        user = self.auth_port.authenticate(credentials)
        if not user:
            raise ValueError("Invalid credentials")
        
        if user.status != "ACTIVE":
            raise ValueError("User is not active")

        # 2. Register or update device Enclave details
        device = Device(
            device_id=device_id,
            user_id=user.user_id,
            push_token=push_token,
            public_key_pem=public_key_pem,
            status=DeviceStatus.ACTIVE,
            created_at=int(datetime.datetime.now(datetime.timezone.utc).timestamp())
        )
        self.device_repo.save(device)

        # 3. Generate Session Token (Signed by KMS)
        return self.token_generator.generate_token(user, device)
