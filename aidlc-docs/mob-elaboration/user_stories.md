# User Stories

## ST-01: Autenticación, Registro de Enclave y Push Tokens
**Como** usuario corporativo,
**Quiero** autenticarme en la aplicación y registrar mi dispositivo móvil,
**Para** obtener un JWT de sesión, registrar mi llave pública (Enclave Seguro) para futuras firmas y registrar mi token de notificaciones (FCM/APNs), cumpliendo PCI-DSS.

**Criterios de Aceptación (AC):**
- **AC1:** El sistema valida credenciales invocando el API REST legado a través de la Capa Anticorrupción (ACL). La autenticación hacia el legado se realiza inyectando una API KEY almacenada de forma segura (AWS Secrets Manager) (Cumplimiento EGS 1.4, **NFR-02**).
- **AC2:** El backend genera un JWT (sin datos sensibles ni PII) y almacena la llave pública del dispositivo generada por el Enclave Seguro (**NFR-02**).
- **AC3:** El backend recibe y almacena de forma segura el Push Token del dispositivo asociándolo al usuario autenticado.
- **AC4:** Las credenciales en tránsito se transmiten estrictamente por TLS 1.2+ y los PINs/Passwords nunca se registran en logs (**NFR-02**).

## ST-02: Inicio de Transferencia Interbancaria y Validación Síncrona
**Como** usuario corporativo iniciador,
**Quiero** registrar una solicitud de transferencia interbancaria donde el sistema valide en tiempo real al titular destino,
**Para** asegurar que los fondos se envíen a la persona correcta, dejando la operación en espera de firmas.

**Criterios de Aceptación (AC):**
- **AC1:** Consulta síncrona a la entidad interbancaria. El procesamiento **interno** de AWS debe resolverse en **<200 ms** (**NFR-01**).
- **AC2:** Resiliencia: Si la entidad externa supera el *timeout* máximo configurado (ej. 2s), el circuito corta la llamada y rechaza la transferencia inmediatamente para evitar contención de infraestructura (**NFR-04**).
- **AC3:** Transacción pasa a `PENDING_APPROVAL` persistida en Amazon DynamoDB. Los datos bancarios sensibles deben estar cifrados (KMS) (**NFR-02**).
- **AC4:** Registro de auditoría inmutable (usuario, fecha/hora, IP) del inicio de la transferencia (**NFR-03**).

## ST-03: Aprobación/Rechazo Multi-firma de Transferencia (Firma de Enclave)
**Como** usuario corporativo aprobador,
**Quiero** aprobar o rechazar criptográficamente una transferencia en estado `PENDING_APPROVAL`,
**Para** ejecutar la transacción si se alcanzan las firmas, o abortarla de inmediato si decido rechazarla.

**Criterios de Aceptación (AC):**
- **AC1:** El backend valida la firma asimétrica del payload usando la llave pública del Enclave Seguro.
- **AC2:** Control de idempotencia (Condición de escritura en DynamoDB) por usuario y transacción. Log inmutable y sincronizado en tiempo por cada acción (**NFR-03**).
- **AC3:** Si el usuario aprueba y se alcanza el umbral de N firmas, el estado cambia a `APPROVED` y se emite el evento de ejecución.
- **AC4:** Si **un solo aprobador** rechaza la transacción, esta cambia inmediatamente a estado `CANCELLED` y se aborta el flujo para todos.

## ST-04: Pago de Facturas Asíncrono y Compensación (Saga Pattern)
**Como** usuario corporativo,
**Quiero** solicitar el pago de una factura de forma asíncrona,
**Para** que el sistema gestione la comunicación inestable con el proveedor externo y, si falla definitivamente, me devuelva los fondos.

**Criterios de Aceptación (AC):**
- **AC1:** La solicitud se encola y devuelve un ID asíncrono al cliente inmediatamente (latencia mínima en UI).
- **AC2:** El orquestador ejecuta el **Paso 1**: Débito en el Core Bancario. Si falla (ej. fondos insuficientes), la Saga se marca como `FAILED` y se emite evento para notificar al usuario.
- **AC3:** Si el Paso 1 es exitoso, el orquestador ejecuta el **Paso 2**: Pago al proveedor externo gestionando retries con Backoff Exponencial y Circuit Breaker (**NFR-04**).
- **AC4:** Si el Paso 2 es exitoso, el estado final es `COMPLETED`. Si el Paso 2 sufre un fallo definitivo (agotados los reintentos), se ejecuta una transacción de **compensación (reverso de fondos)** en el Core Bancario y se marca como `FAILED`.

## ST-05: Sistema Centralizado de Notificaciones Push
**Como** usuario corporativo,
**Quiero** recibir una notificación push en mi dispositivo,
**Para** enterarme en tiempo real cuando una de mis transferencias es ejecutada/rechazada, o cuando un pago de factura finaliza (éxito o fallo).

**Criterios de Aceptación (AC):**
- **AC1:** El servicio escucha eventos de dominio (`TransferApproved`, `TransferCancelled`, `BillPaymentCompleted`, `BillPaymentFailed`).
- **AC2:** Al consumir el evento, recupera los Push Tokens (almacenados en ST-01) de los usuarios involucrados.
- **AC3:** Envía la notificación vía AWS SNS hacia FCM/APNs sin incluir datos transaccionales sensibles en el payload de la notificación (Req PCI).
