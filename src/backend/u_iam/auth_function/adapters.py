import os
import json
import base64
import datetime
import requests
import boto3
from domain import (
    LegacyAuthPort, DeviceRepositoryPort, TokenGeneratorPort, 
    LegacyCredentials, User, Device, JWT, DeviceStatus
)

class SecretManagerLegacyAuthAdapter(LegacyAuthPort):
    def __init__(self, secret_id: str, legacy_api_url: str):
        self.secret_id = secret_id
        self.legacy_api_url = legacy_api_url
        self.client = boto3.client('secretsmanager')
        self._api_key = None

    def _get_api_key(self) -> str:
        if not self._api_key:
            response = self.client.get_secret_value(SecretId=self.secret_id)
            secret_dict = json.loads(response['SecretString'])
            self._api_key = secret_dict.get('API_KEY')
        return self._api_key

    def authenticate(self, credentials: LegacyCredentials) -> User:
        # Anticorruption Layer: Translates local call to Legacy REST API
        api_key = self._get_api_key()
        
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "usuario": credentials.username,
            "clave": credentials.password
        }
        
        # NOTE: In a real environment, handle timeouts and retries
        response = requests.post(
            f"{self.legacy_api_url}/v1/login",
            json=payload,
            headers=headers,
            timeout=5.0
        )
        
        if response.status_code == 200:
            data = response.json()
            # Map legacy format to Domain User
            return User(
                user_id=data.get("id_cliente"),
                role=data.get("perfil", "CORPORATE_USER"),
                status="ACTIVE" if data.get("estado") == "ACTIVO" else "INACTIVE"
            )
        return None

class DynamoDBDeviceRepositoryAdapter(DeviceRepositoryPort):
    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def save(self, device: Device) -> None:
        self.table.put_item(
            Item={
                'PK': f"USER#{device.user_id}",
                'SK': f"DEVICE#{device.device_id}",
                'PushToken': device.push_token,
                'PublicKeyPEM': device.public_key_pem,
                'Status': device.status.value,
                'CreatedAt': device.created_at,
                'Type': 'Device'
            }
        )

    def find_by_user_and_device(self, user_id: str, device_id: str) -> Device:
        response = self.table.get_item(
            Key={
                'PK': f"USER#{user_id}",
                'SK': f"DEVICE#{device_id}"
            }
        )
        item = response.get('Item')
        if not item:
            return None
        return Device(
            device_id=device_id,
            user_id=user_id,
            push_token=item.get('PushToken'),
            public_key_pem=item.get('PublicKeyPEM'),
            status=DeviceStatus(item.get('Status')),
            created_at=item.get('CreatedAt')
        )

class KMSAsymmetricTokenGeneratorAdapter(TokenGeneratorPort):
    def __init__(self, kms_key_id: str):
        self.kms_key_id = kms_key_id
        self.client = boto3.client('kms')

    def generate_token(self, user: User, device: Device) -> JWT:
        # Standard JWT header for RS256/KMS
        header = {
            "alg": "RS256",
            "typ": "JWT"
        }
        
        # Token expires in 1 hour
        expires_in = 3600
        now = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
        exp = now + expires_in
        
        payload = {
            "sub": user.user_id,
            "role": user.role,
            "deviceId": device.device_id,
            "iat": now,
            "exp": exp
        }
        
        # Base64Url encode header and payload
        def b64url(data: dict) -> str:
            return base64.urlsafe_b64encode(json.dumps(data).encode('utf-8')).decode('utf-8').rstrip('=')
            
        header_b64 = b64url(header)
        payload_b64 = b64url(payload)
        message = f"{header_b64}.{payload_b64}"
        
        # Sign with AWS KMS (Asymmetric RSA)
        response = self.client.sign(
            KeyId=self.kms_key_id,
            Message=message.encode('utf-8'),
            MessageType='RAW',
            SigningAlgorithm='RSASSA_PKCS1_V1_5_SHA_256'
        )
        
        signature_b64 = base64.urlsafe_b64encode(response['Signature']).decode('utf-8').rstrip('=')
        jwt_token = f"{message}.{signature_b64}"
        
        return JWT(token=jwt_token, expires_at=exp)
