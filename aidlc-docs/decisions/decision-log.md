# AI-DLC Decision Log Template

> **Version:** 2.0 | **Last Updated:** 2026-02-24  
> **Usage:** One file per session. Log every significant decision made during any AI-DLC ritual.  

---

## Session Info

| Field | Value |
|-------|-------|
| **Session Type** | [Mob Elaboration / Mob Construction / Code Elevation] |
| **Intent** | [Brief description] |
| **Date** | [YYYY-MM-DD] |
| **Participants** | [Names and roles] |
| **Facilitator** | [Name] |

---

## Decisions

### Decision 001
| Field | Detail |
|-------|--------|
| **Phase/Stage** | [e.g., Mob Elaboration — Unit Division] |
| **Decision** | [What was decided] |
| **Context** | [Why this decision was needed] |
| **Options Considered** | [What alternatives were on the table] |
| **Rationale** | [Why this option was chosen over others] |
| **Trade-offs Accepted** | [What we gave up or accepted as risk] |
| **Decided By** | [Who made the call — PO, Dev, Team consensus] |
| **Compatibility Impact** | [Brownfield only: which existing components/interfaces are affected?] |

---

### Decision 002
| Field | Detail |
|-------|--------|
| **Phase/Stage** | |
| **Decision** | |
| **Context** | |
| **Options Considered** | |
| **Rationale** | |
| **Trade-offs Accepted** | |
| **Decided By** | |
| **Compatibility Impact** | [Brownfield only] |

---

### Decision 003
| Field | Detail |
|-------|--------|
| **Phase/Stage** | |
| **Decision** | |
| **Context** | |
| **Options Considered** | |
| **Rationale** | |
| **Trade-offs Accepted** | |
| **Decided By** | |
| **Compatibility Impact** | [Brownfield only] |

---

*Copy the Decision block above for additional entries.*

---

## Notes

- Log decisions as they happen during the session — don't try to reconstruct after.
- Not every micro-decision needs logging. Focus on: Unit splits, architecture choices, NFR thresholds, risk acceptance, scope changes.
- For Brownfield sessions, the "Compatibility Impact" field traces decisions back to the compatibility impact map.
- For Construction-phase architecture decisions, use this log AND create formal ADRs in mob-construction/[bolt]/logical_design.md.
- This log provides the traceability the AI-DLC methodology requires — from Intent to decision to artifact.

## Decision Registry

| ID | Tema | Decisión | Alternativa Rechazada |
|---|---|---|---|
| **D1** | **Mecanismo Soft-Token** | Firma asimétrica mediante Enclave Seguro del dispositivo. El backend valida llave pública. | TOTP (código de 6 dígitos) |
| **D2** | **Gestión de Push Tokens** | El backend en AWS almacena y asocia los tokens de FCM/APNs. | Delegar administración al sistema Legado |
| **D3** | **Regla Multi-firma** | Aborto inmediato (`CANCELLED`) ante el primer rechazo de cualquier aprobador. | Mantener pendiente hasta acumular respuestas |
| **D4** | **Patrón de Pagos (Saga)** | Opción B (Asíncrona pura). Step Functions orquesta el débito interno y luego el pago. Reverso/Compensación en caso de fallo externo. | Opción A (Débito síncrono previo) |
| **D5** | **Latencia Síncrona** | El SLA <200ms aplica solo a la capa interna AWS. Fallo rápido (Timeout Circuit Breaker) en 2s para la entidad externa. | SLA End-to-End estricto (rechazado por alta inestabilidad externa) |
| **D6** | **Integración Legada** | API REST protegida mediante API KEY inyectada desde AWS Secrets Manager. | Basic Auth o IAM puro no soportado |
| **D7** | **Persistencia de Estado** | Amazon DynamoDB (Single Table Design) por sus requerimientos de ultra baja latencia. | Amazon Aurora Serverless |
| **D8** | **Core Bancario** | Se añade un Actor externo (Sistema de Cuentas) para ejecución de los débitos y créditos (Saga compensación). | Ignorar el manejo contable de fondos |
| **D9** | **Parametrización EGS** | Toda URL en Parameter Store. Toda credencial en Secrets Manager. PCI-DSS obliga a Zero Trust y no PII en logs. | ClickOps o variables de entorno en plano |
