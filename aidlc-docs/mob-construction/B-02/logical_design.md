# Logical Design: B-02 (U-TRANS)

## 1. Arquitectura de Infraestructura (AWS Serverless)
- **API Gateway (REST):** Endpoint `/api/v1/transfers`. Incorpora un **JWT Authorizer** para validación Zero-Trust perimetral.
- **AWS Lambda (`TransferFunction`):** Lógica de inicialización. Con Provisioned Concurrency para latencia baja.
- **Amazon DynamoDB (`CoreTable`):**
  - PK: `USER#{userId}`
  - SK: `TX#{transactionId}`
  - Protegido en reposo con AWS KMS (Server-Side Encryption).
- **Interbank API Adapter:** Implementa **Fail-Fast** con un timeout de 1.5s estricto para evitar ataques de agotamiento de recursos (DDoS interno).

## 2. API Contract
### `POST /api/v1/transfers`

**Headers Requeridos**
- `Authorization: Bearer <JWT>`

**Request Payload (`application/json`)**
```json
{
  "destinationBankId": "string (required)",
  "destinationAccount": "string (required)",
  "amount": "number (required, >0)"
}
```

**Response Payload (`202 Accepted`)**
```json
{
  "transactionId": "TX-uuid",
  "status": "PENDING_APPROVAL",
  "message": "Validación interbancaria exitosa. Esperando firmas del Enclave."
}
```
