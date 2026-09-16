# Risk & NFR Analysis

## Requerimientos No Funcionales (NFRs)
- **NFR-01 (Latencia):** El procesamiento interno de transferencias síncronas debe responder en <200ms (p99).
- **NFR-02 (Seguridad):** Cumplimiento estricto de PCI-DSS. Todos los datos sensibles en tránsito (TLS 1.2+) y en reposo (AWS KMS).
- **NFR-03 (Observabilidad):** 100% de operaciones de transferencia y firma deben generar audit logs inmutables.
- **NFR-04 (Resiliencia):** Componentes externos deben aislarse mediante Circuit Breaker y Timeout estricto.
- **NFR-05 (Escalabilidad):** Capacidad de soportar picos transaccionales sin pre-provisionamiento (Serverless).

## Matriz de Riesgos Arquitectónicos

| ID | Riesgo Identificado | Tipo | Impacto | Mitigación Arquitectónica |
|----|---------------------|------|---------|---------------------------|
| **R-01** | **Incumplimiento de SLA por Dependencia Externa:** El banco destino o el Core Bancario demoran > 200ms en responder. | Integración | Alto | Implementar *Fail-Fast Timeout* estricto en el API Gateway y un *Circuit Breaker* en el adaptador Hexagonal de `U-TRANS` (**ST-02**). |
| **R-02** | **Inconsistencia de Estado en Saga:** El orquestador (Step Functions) falla inesperadamente entre el débito del Core y el pago al Facturador, dejando fondos bloqueados. | Estructural | Crítico | Configurar AWS Step Functions en modo **Standard** (garantiza persistencia de estado por hasta 1 año). Uso de DynamoDB condicional para asegurar idempotencia (**ST-04**). |
| **R-03** | **Pérdida/Robo de Dispositivo Físico:** Un usuario pierde el móvil; su llave pública registrada en el Enclave sigue viva permitiendo firmas no autorizadas. | Seguridad | Alto | Habilitar un endpoint en `U-IAM` (invocado por el Admin Portal o el sistema Legado) para revocar explícitamente la llave pública y forzar re-enrolamiento (**ST-01**). |
| **R-04** | **Fugas de Datos (PCI-DSS) en Logs:** Un desarrollador registra accidentalmente el JWT o el payload de la firma en texto claro en AWS CloudWatch. | Seguridad | Crítico | Implementar un *Logger Middleware* obligatorio a nivel de infraestructura que enmascare (scrubbing) campos sensibles y PII antes de emitir a stdout (**ST-01, ST-02**). |
| **R-05** | **Latencia por Cold Start de Lambdas:** Tras periodos de inactividad, el primer request a las funciones Lambda sufre penalización de tiempo ("cold start"), rompiendo el SLA de <200ms. | Rendimiento | Medio | Configurar **Provisioned Concurrency** (Concurrencia Provisionada) en AWS Lambda específicamente para la unidad síncrona `U-TRANS`, garantizando que haya instancias "calientes" siempre disponibles (**ST-02**). |
