# Logical Design: B-04 (U-PAY / Iniciación)

## 1. Arquitectura de Infraestructura
- **API Gateway:** `POST /api/v1/payments`. JWT Authorizer activado.
- **AWS Lambda (`InitiatePaymentFunction`):** API síncrona muy rápida. Solo crea el registro en DynamoDB, empuja un mensaje a SQS y retorna HTTP 202. 
- **Amazon SQS (`PaymentCommandsQueue`):** Cola de mensajes estándar que asegura que ningún pago se pierda ante picos de tráfico.
- **Amazon DynamoDB:** PK=`USER#{userId}`, SK=`PAY#{paymentId}`.

## 2. API Contract
### `POST /api/v1/payments`

**Headers**
- `Authorization: Bearer <JWT>`

**Request Payload**
```json
{
  "billerId": "string (ID de la empresa de servicios)",
  "accountNumber": "string",
  "amount": "number (>0)"
}
```

**Response (`202 Accepted`)**
```json
{
  "paymentId": "PAY-uuid",
  "status": "QUEUED",
  "message": "Pago recibido y encolado para procesamiento asíncrono."
}
```
