# Logical Design: B-03 (U-TRANS / Multi-sig)

## 1. Arquitectura de Infraestructura
- **API Gateway:** `POST /api/v1/transfers/{transactionId}/sign`. Protegido por JWT Authorizer.
- **AWS Lambda (`SignatureFunction`):** Ejecuta la validación matemática.
- **Amazon EventBridge:** Bus de eventos (Event Bus). Recibe el evento `TransferApproved`. Desacopla U-TRANS de U-PAY (Saga Pattern).
- **Amazon DynamoDB:** 
  - Consulta `PK=USER#{userId}, SK=DEVICE#{deviceId}` para extraer el `publicKeyPEM`.
  - Actualiza `PK=USER#{userId}, SK=TX#{transactionId}` a `Status=APPROVED`.

## 2. API Contract
### `POST /api/v1/transfers/{transactionId}/sign`

**Headers**
- `Authorization: Bearer <JWT>`

**Request Payload**
```json
{
  "deviceId": "string (UUID del dispositivo firmante)",
  "signatureBase64": "string",
  "payloadHash": "string (SHA256 del challenge original)"
}
```

**Response (`200 OK`)**
```json
{
  "transactionId": "TX-uuid",
  "status": "APPROVED",
  "message": "Firma validada matemáticamente. Transferencia encolada para ejecución."
}
```
