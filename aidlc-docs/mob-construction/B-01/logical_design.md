# Logical Design: B-01 (U-IAM / Core Auth & Enclave Registry)

## 1. Arquitectura de Infraestructura (AWS Serverless)
- **API Gateway (REST):** Punto único de entrada. Expone el endpoint público `/api/v1/auth/login`. Protegido por WAF.
- **AWS Lambda (`AuthFunction`):** Lógica de negocio (Python 3.12+). Para mitigar el cold-start y cumplir con NFR-01 (<200ms), utilizará **Provisioned Concurrency**.
- **Amazon DynamoDB (`CoreTable`):** Tabla de diseño único (Single Table Design) con On-Demand Capacity.
  - PK: `USER#{userId}`
  - SK: `DEVICE#{deviceId}`
- **AWS Secrets Manager:** Almacena el `LEGACY_API_KEY` necesario para invocar el Core Bancario.
- **AWS KMS (Key Management Service):** Gestiona la llave asimétrica (RSA_2048) para firmar los JWT. La llave privada nunca sale de AWS (Decisión D13).

## 2. API Contract
### `POST /api/v1/auth/login`

**Request Payload (`application/json`)**
```json
{
  "username": "string (required)",
  "password": "string (required, plain text within TLS)",
  "deviceId": "string (required, UUID)",
  "pushToken": "string (required)",
  "publicKeyPEM": "string (required, PEM encoded)"
}
```

**Response Payload (`200 OK`)**
```json
{
  "accessToken": "string (JWT)",
  "expiresIn": 3600
}
```

**Errores**
- `400 Bad Request`: Faltan campos requeridos.
- `401 Unauthorized`: Credenciales inválidas devueltas por el Legacy API.
- `500 Internal Server Error`: Falla de conectividad con dependencias internas.
