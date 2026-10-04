# ADR-002: Usar PostgreSQL como almacenamiento principal

- Estado: Aceptado
- Fecha: 2026-10-03
- Decisores: Kennedy, Diego y Nagin

## Contexto

Los pedidos pueden incluir productos de varios puestos y deben conservar estados, pagos y entregas de forma auditable (RF-02, RF-03, RF-04, RF-06, RF-07 y R-06). El modelo debe distinguir pedido, puesto, item, usuario, pago, entrega y notificacion, sin perder la relacion entre ellos (R-07). El MVP tiene presupuesto bajo (R-03), debe estar operativo en un mes (R-01) y necesita mantener los pedidos aunque WhatsApp no responda (QA-02).

La base tambien debe soportar las consultas del catalogo y del carrito bajo la meta de rendimiento QA-03. No se almacenaran contrasenas en texto plano ni secretos de integracion en la base de datos; se conservaran referencias seguras y estados auditables (R-08).

## Alternativas consideradas

1. **PostgreSQL:** base de datos relacional con transacciones, restricciones, indices y herramientas maduras de migracion.
2. **MongoDB:** base documental con esquemas mas flexibles, pero con consistencia entre documentos relacionados que debe diseniarse cuidadosamente para pedidos multi-puesto.
3. **SQLite en el servidor:** alternativa simple para un prototipo local, pero limitada para concurrencia, crecimiento y operacion multiusuario del MVP.

### Comparacion cualitativa

| Criterio | PostgreSQL | MongoDB | SQLite |
|---|---|---|---|
| Integridad de pedido multi-puesto | Alta | Media, requiere diseño adicional | Media |
| Transacciones y auditoria | Alta | Alta, con modelado cuidadoso | Alta local |
| Operacion en un VPS | Alta | Media | Alta inicialmente |
| Consultas relacionales | Alta | Media | Alta en pequena escala |
| Crecimiento multiusuario | Alta | Alta | Baja |

## Decision

Usaremos **PostgreSQL** como almacenamiento principal. Separaremos logicamente los datos de Catalogo, Pedidos, Pagos y Entregas mediante tablas, claves foraneas e indices. El registro del pedido y sus items se confirmara en una transaccion; las notificaciones quedaran registradas con estado pendiente, enviado o fallido para permitir reintentos.

El modelo minimo incluira `usuarios`, `puestos`, `productos`, `pedidos`, `pedido_items`, `pagos`, `entregas` y `notificaciones`. `pedido_items` conservara el puesto de cada producto para representar correctamente un carrito multi-puesto. Los estados se modelaran como valores controlados y cada cambio relevante incluira fecha y actor.

Las fotos de productos se almacenaran en un servicio de archivos o almacenamiento de objetos; PostgreSQL guardara solo la referencia. Las credenciales, tokens y secretos se administraran mediante variables de entorno o un gestor de secretos, nunca mediante datos de prueba versionados.

### Criterios de cumplimiento

- El pedido y sus items se crean dentro de una transaccion o se revierten completamente.
- Existen indices para puesto, disponibilidad, categoria y estado del pedido.
- El intento de notificacion se persiste antes de invocar al servicio externo.
- Las migraciones se versionan y pueden ejecutarse de forma reproducible en el entorno de prueba.

## Consecuencias

- Positivas: integridad referencial entre pedidos, items y puestos; transacciones para evitar pedidos incompletos; consultas auditables y tecnologia apropiada para el alcance del MVP.
- Positivas: permite indexar catalogos por puesto y disponibilidad para apoyar QA-03.
- Positivas: facilita consultas operativas para reclamos, conciliacion de pagos y seguimiento de entregas.
- Negativas / riesgos: cambios de esquema requieren migraciones y una estructura relacional puede ser menos flexible para futuros datos no estructurados.
- Negativas / riesgos: un indice mal elegido o consultas sin paginacion puede afectar el p95 del catalogo.
- Mitigacion: versionar migraciones, crear indices a partir de pruebas de consulta, usar paginacion y revisar planes de ejecucion.
- Mitigacion: almacenar archivos o fotos fuera de la base de datos y aplicar respaldos periodicos con una prueba de restauracion.

## Plan de respaldo y revision

Durante el MVP se definira una copia de respaldo diaria y se verificara una restauracion al menos una vez antes de la entrega. La decision se revisara si el volumen, la disponibilidad requerida o la necesidad de consultas no relacionales supera las capacidades operativas acordadas.
