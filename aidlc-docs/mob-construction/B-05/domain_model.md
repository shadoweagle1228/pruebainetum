# Domain Model: B-05 (U-PAY / Saga Orchestrator)

## Entidades
- **BillPayment:** Se recupera del repositorio. 
- **BillPaymentStatus:** La máquina de estados transita de `QUEUED` -> `DEBITING` -> `PAYING` -> `COMPLETED`. En caso de fallo transita a `COMPENSATING` y finalmente `FAILED`.

## Puertos (Clean Architecture)
- **SagaOrchestratorUseCase (In):** Caso de uso principal. Orquesta las llamadas secuenciales.
- **PaymentRepositoryPort (Out):** Actualiza el estado de la saga en la base de datos.
- **CoreBankingPort (Out):** Adaptador hacia el banco. Provee métodos `debit()` y `credit()` (reverso).
- **BillerPort (Out):** Adaptador hacia el ente facturador externo. Provee método `pay()`.

```mermaid
classDiagram
    class SagaOrchestratorUseCase {
        <<interface>>
        +execute_payment_saga(paymentId, userId) void
    }
    class CoreBankingPort {
        <<interface>>
        +debit(accountId, amount) boolean
        +credit(accountId, amount) boolean
    }
    class BillerPort {
        <<interface>>
        +pay(billerId, accountId, amount) boolean
    }
    class PaymentRepositoryPort {
        <<interface>>
        +get_payment(paymentId, userId) BillPayment
        +update_status(paymentId, userId, status) void
    }
    
    SagaOrchestratorUseCase --> CoreBankingPort : debita/reversa
    SagaOrchestratorUseCase --> BillerPort : paga
    SagaOrchestratorUseCase --> PaymentRepositoryPort : actualiza
```
