# Domain Model: B-01 (U-IAM / Core Auth & Enclave Registry)

## Entidades y Agregados
- **User:** Representa la identidad corporativa validada.
- **Device:** Representa el dispositivo físico. Almacena la llave pública del Enclave (`publicKeyPEM`) y el token para notificaciones (`pushToken`).
- **DeviceStatus:** Enum para controlar si un dispositivo está `ACTIVE` o `REVOKED`.

## Value Objects
- **JWT:** Token de sesión efímero generado internamente.
- **LegacyCredentials:** Objeto de transporte para credenciales que viajan hacia la Capa Anticorrupción (ACL).

## Puertos (Clean Architecture)
- **AuthenticationUseCase (In):** Orquesta el login, delegando la validación al Legado y el registro del dispositivo al repositorio.
- **LegacyAuthPort (Out):** Adaptador hacia el sistema bancario antiguo.
- **DeviceRepositoryPort (Out):** Adaptador de persistencia para guardar dispositivos registrados.
- **TokenGeneratorPort (Out):** Adaptador de generación criptográfica del JWT.

```mermaid
classDiagram
    class AuthenticationUseCase {
        <<interface>>
        +login(username, password, deviceData) JWT
    }
    class DeviceManagementUseCase {
        <<interface>>
        +revokeDevice(deviceId) void
    }
    class User {
        +String userId
        +String role
        +String status
    }
    class Device {
        +String deviceId
        +String userId
        +String pushToken
        +String publicKeyPEM
        +DeviceStatus status
    }
    class DeviceStatus {
        <<enumeration>>
        ACTIVE
        REVOKED
    }
    class JWT {
        +String token
        +long expiresAt
    }
    class LegacyCredentials {
        +String username
        +String password
    }
    class LegacyAuthPort {
        <<interface>>
        +authenticate(LegacyCredentials) User
    }
    class DeviceRepositoryPort {
        <<interface>>
        +save(Device) void
        +findByUserId(userId) List~Device~
    }
    class TokenGeneratorPort {
        <<interface>>
        +generateToken(User, Device) JWT
    }
    AuthenticationUseCase --> User : maneja
    AuthenticationUseCase --> Device : registra
    AuthenticationUseCase --> LegacyAuthPort : usa
    AuthenticationUseCase --> TokenGeneratorPort : usa
    AuthenticationUseCase --> DeviceRepositoryPort : usa
    Device --> DeviceStatus : tiene
```
