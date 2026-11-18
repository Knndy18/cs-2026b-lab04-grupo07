# ADR-007: Patrón Transaccional Outbox para Resiliencia ante Caídas de Pasarelas

- Estado: Aceptado
- Fecha: 2026-10-29
- Decisores: Kennedy, Diego y Nagin (Grupo 07)
- Escenario Atendido: `QA-03` (Disponibilidad: Caída de Yape/Plin de 20 min con 0 pedidos perdidos)
- Iteración ADD: Iteración 2 (Disponibilidad)

## Contexto

Las pasarelas de pago móvil (Yape y Plin) y los servicios de mensajería (WhatsApp Business API) son sistemas externos fuera del control del equipo que sufren caídas intermitentes o picos de latencia en horas pico. 
En el diseño inicial, la confirmación del pedido ejecutaba una verificación síncrona por HTTP hacia la pasarela. Durante una interrupción de 20 minutos del servicio externo, las solicitudes de los clientes fallaban con errores 500, bloqueando las ventas de los comerciantes y provocando la pérdida irremediable de pedidos confirmados, violando el atributo crítico de disponibilidad y fiabilidad (`QA-03`) y la restricción operativa de auditoría (`R-06`).

## Alternativas consideradas

1. **Reintentos Síncronos Bloqueantes en el Endpoint HTTP:** Reintentar en un bucle con `sleep` dentro de la petición web.
   * *Descarte:* Agota rápidamente el pool de workers de Gunicorn (4 workers), provocando la caída completa de todo el sistema por bloqueo de hilos (*Cascading Failure*).
2. **Cola de Reintentos Exclusivamente en Memoria Volátil (Redis Pub/Sub):**
   * *Descarte:* Si el contenedor de Redis o el servidor VPS se reinicia durante la caída de la pasarela, todos los pagos y pedidos pendientes en memoria se pierden irrecuperablemente.
3. **Patrón Transaccional Outbox en PostgreSQL + Celery Worker (Tácticas: Degradación Agraciada y Encolado Persistente):**
   * *Ventajas:* El pedido y el evento de cobro pendiente se insertan de forma atómica en la misma transacción ACID en la base de datos relacional. Un worker en segundo plano consume los registros pendientes con reintentos exponenciales y *Circuit Breaker*.

## Decisión

Implementar el **Patrón Transaccional Outbox** (`Transactional Outbox Pattern`) junto con un **Circuit Breaker** para el procesamiento de pagos y notificaciones externas:

1. Cuando la pasarela externa responde con timeout o error 5xx, el circuito se abre (*Fail Fast*).
2. El sistema guarda el pedido con estado `PENDIENTE_PAGO_ASINCRONO` y registra un mensaje en la tabla `pagos_outbox` dentro de una **única transacción atómica** de PostgreSQL.
3. El cliente recibe una confirmación provisional de recepción de pedido con código HTTP 202 Accepted.
4. El contenedor `worker` (Celery) lee periódicamente los registros pendientes de `pagos_outbox` y reintenta la verificación con retroceso exponencial (*exponential backoff* con jitter) hasta 5 veces.
5. Al verificar el pago, actualiza el estado a `PAGADO` y emite el evento de notificación a los comerciantes.

La decisión está respaldada por la simulación estocástica Monte Carlo de 1,000 iteraciones (`fitness/disponibilidad.py`), la cual arrojó:
- **Pedidos Perdidos:** **0 pedidos perdidos** ($100\%$ de resiliencia).
- **Tasa de Recuperación:** $100\%$ de los pedidos pendientes fueron regularizados en un tiempo medio de recuperación de $1.2\text{ minutos}$ tras el restablecimiento del servicio.

## Consecuencias

* **Positivas:** Cumplimiento total de `QA-03` ($0$ pedidos perdidos), protección de la experiencia de usuario y resiliencia absoluta frente a terceros no confiables (`R-05`).
* **Negativas / Trade-off:** Se traslada la confirmación final a un modelo de consistencia eventual (`T2`). El cliente no recibe el comprobante definitivo en tiempo real durante la caída, sino cuando el servicio externo se restablece.
* **Mitigación:** La interfaz PWA informa al usuario de manera transparente: *"Tu pedido ha sido recibido y tu pago está en cola de verificación automática"*.

## Plan de evolución y monitoreo

Se integra la Fitness Function `fitness/disponibilidad.py` en el pipeline de GitHub Actions para certificar que ante cualquier cambio de configuración, la pérdida de pedidos permanezca estrictamente en cero.
