# ADR-003: Autenticacion por cuenta y autorizacion por rol

- Estado: Aceptado
- Fecha: 2026-10-03
- Decisores: Kennedy, Diego y Nagin

## Contexto

El sistema tiene tres actores operativos con permisos diferentes: cliente, comerciante y repartidor, ademas de un administrador (RF-01 a RF-09). Los pedidos, comprobantes y datos de contacto deben estar protegidos contra lectura o modificacion no autorizada (QA-05 y R-08). El comerciante debe completar acciones desde un celular de gama baja (R-04 y QA-01), por lo que el mecanismo de acceso no debe imponer un flujo pesado para cada operacion.

El MVP debe limitar su complejidad y estar listo en un mes (R-01 y R-02). La autorizacion debe considerar tanto el rol como la pertenencia del recurso: un comerciante puede gestionar los productos de su puesto, pero no los de otro puesto; un repartidor puede actualizar una entrega asignada, pero no cambiar el pago.

## Alternativas consideradas

1. **Autenticacion propia con sesiones y roles:** cuentas gestionadas por la aplicacion, contrasenas almacenadas con hash seguro y permisos validados en cada endpoint.
2. **Proveedor externo de identidad desde el inicio:** delegar registro, inicio de sesion y recuperacion de cuenta a un servicio de identidad externo.
3. **Enlaces de acceso enviados por WhatsApp:** autenticar al usuario principalmente mediante codigos de un solo uso enviados por mensajeria.

### Comparacion cualitativa

| Criterio | Sesiones propias | Proveedor externo | Enlaces por WhatsApp |
|---|---|---|---|
| Tiempo de implementacion | Alto | Medio | Medio |
| Control de roles y recursos | Alto | Alto, requiere integracion | Medio |
| Dependencia externa | Baja | Alta | Alta |
| Adecuacion al presupuesto | Alta | Media | Media |
| Recuperacion de cuenta | Debe implementarse | Incluida por el proveedor | Depende de mensajeria |

## Decision

Usaremos autenticacion gestionada por la aplicacion con sesiones seguras y autorizacion basada en roles: `cliente`, `comerciante`, `repartidor` y `administrador`. Las contrasenas se almacenaran unicamente con un algoritmo de hash adecuado; cada endpoint validara identidad, rol y pertenencia del recurso antes de permitir cambios. El acceso administrativo se mantendra separado de las operaciones comerciales.

La politica de autorizacion sera la siguiente:

| Rol | Puede hacer | No puede hacer |
|---|---|---|
| Cliente | Consultar catalogo, crear sus pedidos y consultar su historial. | Editar productos, pedidos de otros clientes o asignaciones de reparto. |
| Comerciante | Gestionar productos de su puesto, aceptar items y revisar pedidos dirigidos a su puesto. | Modificar productos o pedidos de otro puesto. |
| Repartidor | Consultar entregas asignadas y actualizar sus estados. | Cambiar precios, comprobantes o pedidos no asignados. |
| Administrador | Gestionar puestos, usuarios y excepciones operativas auditadas. | Consultar contrasenas o secretos en texto plano. |

La sesion utilizara cookies `HttpOnly`, `Secure` y con politica `SameSite` apropiada. Se aplicara expiracion de sesion, limite de intentos de inicio de sesion y registro de eventos de seguridad sin incluir contrasenas ni tokens. La autorizacion se probara en cada endpoint sensible y no se confiara unicamente en ocultar botones de la interfaz.

### Criterios de cumplimiento

- QA-05 debe alcanzar 100 % de rechazo en la matriz de 30 intentos no autorizados.
- Las contrasenas no aparecen en respuestas, logs, archivos de configuracion ni repositorios.
- Un comerciante solo puede consultar y modificar recursos cuyo `puesto_id` coincida con su asignacion.
- Los eventos de inicio de sesion, cambios de rol y operaciones sensibles quedan registrados con actor y fecha.

## Consecuencias

- Positivas: control directo de permisos, menor dependencia externa y menor costo inicial, coherente con R-01, R-02 y R-03.
- Positivas: evita que un comerciante pueda modificar productos o pedidos de otro puesto y protege los datos de RF-05 a RF-07.
- Positivas: el modelo de roles puede ampliarse sin cambiar la identidad de los usuarios.
- Negativas / riesgos: el equipo debe implementar correctamente recuperacion de cuenta, expiracion de sesiones y proteccion contra intentos repetidos.
- Negativas / riesgos: una regla de autorizacion incompleta puede exponer datos de otro usuario aunque la interfaz parezca correcta.
- Mitigacion: aplicar hash seguro, cookies `HttpOnly` y `Secure`, expiracion de sesion, limite de intentos y pruebas de autorizacion por rol.
- Mitigacion: centralizar las politicas de acceso, revisar cada endpoint y ejecutar pruebas negativas con recursos pertenecientes a otros puestos.

## Plan de revision

La decision se revisara si el numero de roles crece significativamente, si se requiere inicio de sesion institucional o si la recuperacion de cuentas supera la capacidad del equipo. En ese caso se evaluara integrar un proveedor externo sin eliminar la autorizacion de dominio propia.
