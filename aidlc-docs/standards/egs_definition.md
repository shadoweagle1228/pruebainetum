# Enterprise Guardrail System (EGS)

> **Reglas Técnicas y Arquitectónicas de la Organización**
> Todas las fases de diseño y construcción deben cumplir obligatoriamente con estos lineamientos.

## 1. Seguridad e Identidades (Alineación PCI-DSS)
- **1.1 Zero Trust:** Ningún servicio confía en otro por defecto. Todas las peticiones API y eventos entre microservicios deben estar autenticados (IAM o JWT validado).
- **1.2 Cifrado en Tránsito:** Uso estricto de TLS 1.2 o superior en todas las comunicaciones. No se permite tráfico HTTP plano bajo ninguna circunstancia.
- **1.3 Cifrado en Reposo:** Todos los datos (especialmente información bancaria y tokens) deben estar cifrados en reposo utilizando claves gestionadas (ej. AWS KMS).
- **1.4 Manejo de Secretos:** Prohibido escribir secretos (claves, passwords, tokens) en código fuente. Usar bóvedas de secretos (ej. AWS Secrets Manager o Parameter Store).

## 2. Arquitectura de Software
- **2.1 Clean Architecture (Hexagonal):** Separación estricta entre el Core de Dominio y la Infraestructura (Puertos y Adaptadores). La lógica de negocio no debe conocer detalles de la base de datos ni de APIs externas.
- **2.2 Event-Driven Architecture (EDA):** Operaciones asíncronas de larga duración o propensas a fallos (ej. pagos de facturas) deben implementarse mediante orquestación de eventos (ej. SQS/SNS/EventBridge o Step Functions).
- **2.3 Anti-Corruption Layer (ACL):** Todo acceso a sistemas legados debe pasar por una ACL para traducir modelos de datos y proteger el nuevo dominio de conceptos obsoletos.

## 3. Resiliencia y Alta Disponibilidad
- **3.1 SLAs Síncronos:** Toda llamada de API síncrona debe retornar en <200ms. Si excede, debe fallar rápido (Fail-Fast).
- **3.2 Patrones de Tolerancia a Fallos:** Implementar Circuit Breaker y Dead Letter Queues (DLQ) para integraciones externas. Todo reintento debe usar Backoff Exponencial.

## 4. Observabilidad (Alineación PCI-DSS)
- **4.1 Trazabilidad de Auditoría (Audit Trails):** Toda transacción o firma debe generar un log inmutable con: Fecha/Hora (sincronizada vía NTP), Identidad del usuario, Acción y Origen (IP).
- **4.2 Protección de Logs:** **NUNCA** registrar credenciales, PINs, tokens crudos ni PII en texto claro en el sistema de logs (CloudWatch/ELK).
- **4.3 Correlation IDs:** Toda petición entrante al API Gateway debe generar o propagar un ID de correlación único que fluya a través de todos los microservicios y logs.

## 5. Infraestructura Cloud-Native (AWS)
- **5.1 Serverless-First:** Priorizar servicios sin servidor (Lambda, DynamoDB, Fargate, SQS, SNS, API Gateway) para optimizar costos y escalar a cero. Para mitigar el problema de *cold start* en operaciones críticas (SLA <200ms), se permite el uso de **Provisioned Concurrency** en Lambdas clave.
- **5.2 Infraestructura como Código (IaC):** Prohibida la configuración manual (ClickOps). El 100% de la infraestructura de AWS (API Gateway, Lambda, DynamoDB, Step Functions, SQS, SNS, IAM roles) DEBE definirse como código usando **AWS CDK con Python**.
