# Domain Model: B-04 (U-PAY / Iniciación de Pagos)

## Entidades y Value Objects
- **BillPayment:** Representa la intención de pagar un servicio público o privado.
- **BillPaymentStatus:** Estado de la transacción en la saga (`QUEUED`, `DEBITING`, `PAYING`, `COMPLETED`, `FAILED`, `COMPENSATING`).

## Puertos (Clean Architecture)
- **InitiatePaymentUseCase (In):** Caso de uso que valida la estructura básica, asigna un ID único y encola el pago.
- **MessageQueuePort (Out):** Adaptador para enviar el mandato de pago a un sistema de colas asíncrono (AWS SQS), desacoplando la API del procesamiento intensivo.
- **PaymentRepositoryPort (Out):** Persistencia inicial con estado `QUEUED`.

```mermaid
classDiagram
    class InitiatePaymentUseCase {
        <<interface>>
        +initiate(userId, billerId, account, amount) BillPayment
    }
    class BillPayment {
        +String paymentId
        +String userId
        +String billerId
        +String account
        +Decimal amount
        +BillPaymentStatus status
    }
    class BillPaymentStatus {
        <<enumeration>>
        QUEUED
    }
    class MessageQueuePort {
        <<interface>>
        +enqueuePaymentCommand(paymentId) void
    }
    class PaymentRepositoryPort {
        <<interface>>
        +save(BillPayment) void
    }
    
    InitiatePaymentUseCase --> BillPayment : crea
    InitiatePaymentUseCase --> MessageQueuePort : encola
    InitiatePaymentUseCase --> PaymentRepositoryPort : persiste
```
