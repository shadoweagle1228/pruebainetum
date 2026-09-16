import os
import json
import logging
from domain import AuthenticationUseCase, LegacyCredentials
from adapters import (
    SecretManagerLegacyAuthAdapter, 
    DynamoDBDeviceRepositoryAdapter, 
    KMSAsymmetricTokenGeneratorAdapter
)

# Configure logger (PCI-DSS: No logging of raw credentials or PII)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables injected by CDK
TABLE_NAME = os.environ.get('CORE_TABLE_NAME')
LEGACY_API_URL = os.environ.get('LEGACY_API_URL')
LEGACY_SECRET_ID = os.environ.get('LEGACY_SECRET_ID')
KMS_KEY_ID = os.environ.get('KMS_KEY_ID')

# Composition Root (Initialize adapters once during cold start for Provisioned Concurrency)
auth_port = SecretManagerLegacyAuthAdapter(
    secret_id=LEGACY_SECRET_ID, 
    legacy_api_url=LEGACY_API_URL
)
device_repo = DynamoDBDeviceRepositoryAdapter(table_name=TABLE_NAME)
token_generator = KMSAsymmetricTokenGeneratorAdapter(kms_key_id=KMS_KEY_ID)

use_case = AuthenticationUseCase(
    auth_port=auth_port,
    device_repo=device_repo,
    token_generator=token_generator
)

def handler(event, context):
    try:
        # 1. Extract Correlation ID from API Gateway for Audit Trailing
        correlation_id = event.get('requestContext', {}).get('requestId', 'UNKNOWN')
        logger.info(f"Processing login request. CorrelationId: {correlation_id}")
        
        # 2. Parse request body
        body = json.loads(event.get('body', '{}'))
        
        username = body.get('username')
        password = body.get('password')
        device_id = body.get('deviceId')
        push_token = body.get('pushToken')
        public_key_pem = body.get('publicKeyPEM')
        
        if not all([username, password, device_id, push_token, public_key_pem]):
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Missing required fields"})
            }
            
        credentials = LegacyCredentials(username=username, password=password)
        
        # 3. Execute Domain Logic
        jwt_response = use_case.login(
            credentials=credentials,
            device_id=device_id,
            push_token=push_token,
            public_key_pem=public_key_pem
        )
        
        logger.info(f"Login successful for device {device_id}. CorrelationId: {correlation_id}")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "accessToken": jwt_response.token,
                "expiresIn": jwt_response.expires_at
            })
        }
        
    except ValueError as ve:
        logger.warning(f"Domain validation failed: {str(ve)}")
        return {
            "statusCode": 401,
            "body": json.dumps({"message": "Unauthorized"})
        }
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal Server Error"})
        }
