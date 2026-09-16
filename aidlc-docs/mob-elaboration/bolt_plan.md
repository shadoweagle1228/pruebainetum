# Bolt Execution Plan

El siguiente plan de entrega descompone las Unidades en **Bolts** (la unidad mínima de entrega en AI-DLC), organizados secuencialmente desde las capas base (Identidad) hasta las capas superiores (Pagos/Notificaciones).

| Secuencia | Bolt ID | Contexto (Unidad) | Descripción del Valor a Entregar | Historias | Esfuerzo (Horas) | Dependencias |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `B-01` | `U-IAM` | **Core Auth & Enclave Registry:** Integración del API Legada mediante ACL (AWS Secrets Manager), emisión del JWT y registro de la llave pública. Base de Zero Trust. | ST-01 | 12h | Ninguna |
| **2** | `B-02` | `U-TRANS` | **Transfer State Machine & Sync Validation:** Endpoint protegido, validación interbancaria (SLA <200ms) y creación de transacción en `PENDING_APPROVAL`. | ST-02 | 14h | B-01 |
| **3** | `B-03` | `U-TRANS` | **Multi-sig Cryptographic Engine:** Algoritmo de firma asimétrica de Enclave, idempotencia y evaluación del umbral de firmas para `APPROVED` o `CANCELLED`. | ST-03 | 16h | B-01, B-02 |
| **4** | `B-04` | `U-PAY` | **Async Bill Payment Saga:** Orquestación en AWS Step Functions. Paso 1: Débito al Core. Paso 2: Pago a Facturador. Mecanismo de reverso de fondos. | ST-04 | 16h | B-01 |
| **5** | `B-05` | `U-NOTIF` | **Centralized Notification Engine:** Consumidor SQS/EventBridge que enruta notificaciones hacia AWS SNS sin incluir PII (PCI-DSS). | ST-05 | 8h | B-03, B-04 |

## Análisis de Ciclos / Dependencias
- `B-01` no tiene dependencias internas (Capa Base).
- `B-02` y `B-04` requieren el JWT generado en `B-01`.
- `B-03` requiere el estado persistido por `B-02` y la llave pública de `B-01`.
- `B-05` es completamente reactivo y desacoplado; solo requiere consumir eventos emitidos por `B-03` y `B-04`.
- **Resultado:** El grafo de dependencias es estrictamente unidireccional (Acyclic). No hay ciclos bloqueantes.
