# ADR-007: Resiliencia en Pagos mediante Circuit Breaker y Patrón Outbox Transaccional

## Estado
Aceptado

## Contexto
Ante caídas transitorias de las pasarelas externas (QA-03), el sistema no debe perder operaciones de pago ni saturar al proveedor externo.

## Decisión
Se aplica el patrón Decorator sobre el puerto de pagos para incorporar un Circuit Breaker con política de reintentos y persistencia de operaciones pendientes en una tabla Outbox en PostgreSQL (descartando guardar la cola en memoria volátil de Redis).

## Consecuencias y Evidencia
- **Positivo:** La simulación Monte Carlo arroja 0 pedidos perdidos durante una caída simulada de 20 min y reduce las llamadas al proveedor de 180 a 18.
- **Trade-off:** Se introduce consistencia eventual para las transacciones diferidas.
