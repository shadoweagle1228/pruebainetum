# Logical Units (Bounded Contexts)

Basado en Domain-Driven Design (DDD) y los principios de Clean Architecture y Serverless, las Historias de Usuario se han agrupado en los siguientes Contextos Delimitados (Bounded Contexts) o Microservicios.

| Unit ID | Bounded Context (Microservicio) | Responsabilidad Principal (Dominio) | Historias Mapeadas | Puertos y Adaptadores (Clean Arch) |
|---------|--------------------------------|-------------------------------------|--------------------|----------------------------------|
| **U-IAM** | Identity & Security Context | Gestionar la autenticación Zero Trust, validación de API Legada, emisión de JWT y administración de llaves públicas del Enclave Seguro y Push Tokens. | ST-01 | **In:** API Gateway (Login/Device Reg)<br>**Out:** Legacy Auth Adapter (REST), Token Repository (DynamoDB), Secrets Manager Adapter |
| **U-TRANS**| Transfers & Multi-sig Context | Orquestar la máquina de estados de transferencias (`PENDING_APPROVAL`, `APPROVED`, `CANCELLED`), validar topología interbancaria y verificar firmas criptográficas. | ST-02, ST-03 | **In:** API Gateway (Transfers), EventBridge (Sigs)<br>**Out:** Interbank Adapter (REST), State Repo (DynamoDB), Core Bank Adapter (Exec) |
| **U-PAY** | Async Payments Context | Orquestar el patrón Saga para el pago de facturas. Asegurar que los débitos y pagos externos sean transaccionalmente seguros (Saga/Compensación). | ST-04 | **In:** API Gateway (Bill Pay)<br>**Out:** Core Bank Adapter (Debit/Credit), Biller Adapter (REST), Step Functions Orchestrator |
| **U-NOTIF**| Notifications Context | Reaccionar a eventos de dominio de forma asíncrona para despachar mensajes a los dispositivos físicos sin acoplar los dominios transaccionales. | ST-05 | **In:** SQS/EventBridge (Domain Events)<br>**Out:** Device Token Repo (DynamoDB), Push Provider (AWS SNS -> APNs/FCM) |
