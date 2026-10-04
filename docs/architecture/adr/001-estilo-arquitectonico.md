# ADR-001: Adoptar un monolito modular para San Camilo en Linea

- Estado: Aceptado
- Fecha: 2026-10-03
- Decisores: Kennedy, Diego y Nagin

## Contexto

El sistema debe digitalizar las ventas de los puestos del Mercado San Camilo sin exigir una infraestructura compleja. El MVP debe entregarse en un mes (R-01), con un equipo de hasta tres developers (R-02), presupuesto bajo (R-03) y comerciantes que pueden usar celulares de gama baja con conectividad limitada (R-04). Ademas, un carrito puede contener productos de varios puestos (R-07), por lo que los pedidos, sus items y sus estados deben manejarse de forma coherente.

La arquitectura debe favorecer la capacidad de interaccion del comerciante (QA-01), conservar los pedidos cuando falle una integracion externa (QA-02), sostener el rendimiento del catalogo (QA-03), permitir incorporar un nuevo medio de pago (QA-04) y controlar los accesos por puesto (QA-05). Los requisitos funcionales mas directamente relacionados son RF-01 a RF-09, especialmente la publicacion de productos, la confirmacion de pedidos, las notificaciones y la actualizacion de entregas.

## Alternativas consideradas

1. **Monolito en capas:** un solo despliegue con presentacion, servicios, dominio y persistencia compartidos. Tiene bajo costo inicial, pero puede permitir que las reglas y dependencias de todos los dominios se mezclen con el crecimiento.
2. **Monolito modular:** un solo despliegue dividido en Catalogo, Pedidos, Pagos, Notificaciones y Entregas, con interfaces publicas entre modulos. Mantiene la simplicidad operativa, pero exige disciplina para no romper los limites.
3. **Microservicios:** servicios desplegables de forma independiente, con comunicacion por red y posible base de datos por servicio. Favorece el escalamiento independiente, pero agrega despliegues, observabilidad, seguridad de red y consistencia distribuida.

### Comparacion cualitativa

| Criterio | Monolito en capas | Monolito modular | Microservicios |
|---|---|---|---|
| Entrega en un mes | Alta | Alta | Baja |
| Costo de operacion | Bajo | Bajo | Alto |
| Separacion de responsabilidades | Media | Alta | Alta |
| Complejidad de despliegue | Baja | Baja | Alta |
| Evolucion futura | Media | Alta | Alta, con costo inicial alto |
| Adecuacion al equipo de 3 developers | Alta | Alta | Baja |

## Decision

Usaremos un **monolito modular** para el MVP. Los modulos principales seran Catalogo, Pedidos, Pagos, Notificaciones y Entregas. Se desplegaran juntos para reducir la complejidad operativa, pero cada modulo tendra responsabilidades e interfaces explicitas.

La dependencia permitida sera la siguiente: la API de presentacion invoca servicios de aplicacion; cada modulo encapsula sus reglas; los repositorios y adaptadores se ubican en infraestructura. Las integraciones con el proveedor de pago y WhatsApp se aislaran mediante adaptadores, de modo que un cambio de proveedor no obligue a modificar las reglas de Pedidos.

El modulo Pedidos sera el propietario del ciclo de vida del pedido. Notificaciones recibira una solicitud persistida y procesara el envio de forma asincrona o reintentable. Catalogo administrara productos y disponibilidad; Pagos registrara referencias y estados del pago; Entregas gestionara asignaciones y estados del delivery.

### Criterios de cumplimiento

- El despliegue del MVP podra ejecutarse en un unico servidor de bajo costo, cumpliendo R-01, R-02 y R-03.
- Los limites de modulos se revisaran en Pull Requests y no se permitiran accesos directos a tablas o internals de otro modulo.
- Las pruebas de aceptacion de QA-01, QA-02 y QA-03 seran obligatorias antes de declarar estable el MVP.

## Consecuencias

- Positivas: un solo despliegue, menor costo operativo, entrega compatible con R-01 y una base para extraer un modulo en el futuro.
- Positivas: los limites de los modulos facilitan cumplir QA-01, QA-02 y la modificabilidad de nuevos medios de pago o modalidades de pedido.
- Positivas: las transacciones entre tablas relacionadas pueden mantenerse en una misma aplicacion sin introducir llamadas de red para el flujo principal.
- Negativas / riesgos: una falla grave puede afectar a todo el despliegue y los limites pueden degradarse si se permiten dependencias directas entre modulos.
- Negativas / riesgos: el monolito no permite escalar cada modulo de forma independiente si la demanda futura crece de manera desigual.
- Mitigacion: revisar dependencias en Pull Requests, validar interfaces publicas y aplicar pruebas de arquitectura en CI cuando el repositorio de software este disponible.
- Mitigacion: extraer primero el modulo que presente mayor presion de carga, usando los adaptadores y contratos ya definidos.

## Plan de evolucion y revision

La decision se revisara si el sistema supera de forma sostenida el umbral de QA-03, si un modulo requiere despliegues independientes o si el costo de coordinar cambios entre modulos supera el beneficio del despliegue unico. La migracion no se activara por moda: debera sustentarse con metricas de carga, incidentes, tiempos de entrega y capacidad real del equipo.
