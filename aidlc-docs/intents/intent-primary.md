# Intent: Reingeniería de Backend - App Móvil Bancaria Empresarial

**Type:** feature

## Summary

Reingeniería de la arquitectura técnica y backend de una aplicación móvil de banca empresarial. El objetivo es transicionar de un sistema de alta latencia y dependencias legadas síncronas hacia una arquitectura nativa en la nube (AWS), orientada a microservicios/serverless. El nuevo diseño se apoyará fuertemente en Clean Architecture (Ports & Adapters), Event-Driven Architecture (EDA) y Security-Driven Design (Zero Trust) para garantizar escalabilidad, resiliencia (antifragilidad ante integraciones externas) y seguridad avanzada en operaciones corporativas.

## Users / Actors

- **Usuarios Corporativos (Iniciadores y Aprobadores):** Empleados que inician o autorizan transacciones. Cualquier usuario con perfil "aprobador" puede firmar hasta alcanzar el número requerido (no hay jerarquías estrictas).
- **Core Bancario (Sistema de Cuentas):** Sistema externo encargado de los débitos, créditos y reversos de fondos.
- **Entes de Facturación Externos:** Proveedores de servicios para pago de facturas.
- **Sistema Legado de Credenciales:** Repositorio actual del portal web, consumido vía API REST.
- **Entidades Interbancarias:** Sistemas externos para validación de titularidad destino.
- **Sistemas de Notificaciones Push:** APNs / Firebase Cloud Messaging (mediante AWS SNS).

## Key Scenarios

1. **Autenticación y Registro de Enclave:** Login contra la capa anticorrupción (ACL) consumiendo el API REST legado. El nuevo backend registra la llave pública del dispositivo móvil (generada en el Enclave Seguro) y emite un JWT para validación Zero Trust. Adicionalmente, el backend registrará el token de dispositivo (FCM/APNs) para notificaciones push.
2. **Transferencias Interbancarias con Aprobación:** Un usuario inicia una transferencia; el sistema valida sincrónicamente la cuenta destino. La transacción queda en estado `PENDING_APPROVAL`.
3. **Firma Criptográfica y Aborto Rápido:** Los aprobadores firman el payload usando la llave privada de su Enclave Seguro. Si se alcanzan las firmas requeridas, se ejecuta contra el Core Bancario. Si **un solo aprobador** la rechaza, la transacción se aborta inmediatamente (`CANCELLED`).
4. **Pago de Facturas Asíncrono (Saga Pattern):** La app encola la solicitud de pago inmediatamente. Un orquestador (Step Functions) toma el control: **Paso 1** debita los fondos en el Core Bancario; **Paso 2** paga al proveedor externo gestionando reintentos. Si el Paso 1 falla (ej. sin fondos), se aborta la Saga. Si el Paso 2 sufre un fallo definitivo, se ejecuta una transacción de reverso/compensación hacia el Core Bancario.
5. **Notificaciones de Dominio:** Al completarse todas las firmas, abortarse una transacción, o finalizar un pago, se emite un evento que dispara notificaciones push usando los tokens gestionados por el nuevo backend.

## Constraints

- **AWS Well-Architected Framework:** Estricto alineamiento a sus 6 pilares.
- **Clean Architecture:** Separación total de reglas de negocio e infraestructura (Hexagonal).
- **Persistencia (NoSQL):** Uso exclusivo de Amazon DynamoDB para el almacenamiento de estado transaccional buscando latencia ultra baja.
- **Parametrización Dinámica (AWS SSM):** Todos los sistemas externos (Core Bancario, Entidades Interbancarias, Legado, Facturadores) deben ser 100% parametrizables. Las URLs y configuraciones irán en **AWS Parameter Store**, y las credenciales/tokens técnicos obligatoriamente en **AWS Secrets Manager**.
- **Integraciones y Resiliencia:** 
  - Entes de facturación asíncronos: Patrones de Dead Letter Queues (DLQ) y Circuit Breakers.
  - Entes síncronos (Interbancarios/Core): Manejo estricto de *Timeouts* para evitar estrangulamiento si el ente externo es lento.
- **Seguridad (PCI-DSS y Zero Trust):** Cifrado en tránsito (TLS 1.2+ obligatorio) y reposo. Todo diseño debe adherirse a los controles de **PCI-DSS**.
- **Rendimiento (SLA):** El procesamiento **interno** de las operaciones síncronas debe responder en un máximo de **200 ms** (excluyendo el tiempo de latencia de red del proveedor externo).

## Out of Scope

- **Frontend Móvil:** El desarrollo o modificación de las interfaces de la aplicación (iOS/Android) está fuera de alcance. El proyecto es puramente reingeniería backend.
- Modificaciones estructurales al core bancario o sistema legado (nos integraremos consumiendo sus APIs REST actuales).

## Success Criteria

1. Diagrama de Arquitectura de Solución (AWS, red e integraciones) y **Diagrama de Capas Técnicas**.
2. Diseño de Componentes Hexagonales (estructura de paquetes y puertos In/Out) para Pagos y Firmas.
3. Detalle de la solución con descripción exhaustiva y **Diagrama(s) de Secuencia** de apoyo (incluyendo el caso de uso de Transferencia).
4. Matriz de Riesgos y Mitigaciones basada en el nuevo modelo de Token Digital.
5. Sistema backend desplegable en infraestructura Serverless que cumpla el SLA de <200ms en flujos síncronos.
