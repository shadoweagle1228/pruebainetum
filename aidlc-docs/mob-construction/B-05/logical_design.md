# Logical Design: B-05 (U-PAY / Saga Orchestrator)

## 1. Arquitectura de Infraestructura
- **Trigger (Event Source):** Amazon SQS `PaymentCommandsQueue`.
- **AWS Lambda (`SagaWorkerFunction`):** Procesa mensajes en lotes (batch). Está diseñada para ser **idempotente**; si un mensaje se reprocesa, verifica el estado en la base de datos antes de debitar el dinero nuevamente.
- **Amazon DynamoDB (`CoreTable`):** Almacena y bloquea el estado de la saga. Se utiliza bloqueo optimista si es posible, o actualización incondicional del estado (ej. de `QUEUED` a `DEBITING`).
- **Secret Manager:** Contiene las credenciales para el Core Bancario y el Ente Facturador.

## 2. Lógica de la Saga (Flujo Principal y Compensación)
**Paso 1: Transición a DEBITING**
- Se actualiza la BD a `DEBITING`.
- Se llama a `CoreBankingPort.debit()`.
- *Si falla:* Actualiza a `FAILED` (Fin).

**Paso 2: Transición a PAYING**
- Se actualiza la BD a `PAYING`.
- Se llama a `BillerPort.pay()`.
- *Si falla:* Transita a `COMPENSATING`.

**Paso 3: Compensación (Reverso)**
- Se llama a `CoreBankingPort.credit()` para devolver el dinero al usuario.
- Actualiza a `FAILED`.

**Paso 4: Finalización Exitosa**
- Si todo pasa, actualiza a `COMPLETED`.
