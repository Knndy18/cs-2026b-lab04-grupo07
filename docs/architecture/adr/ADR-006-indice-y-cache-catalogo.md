# ADR-006: Incorporación de Índice Compuesto y Caché Redis para el Catálogo

## Estado
Aceptado

## Contexto
El escenario de crecimiento (QA-01) exige soportar la concurrencia en horas pico sin degradar el tiempo de respuesta p95 por encima de los 2.0 segundos.

## Decisión
Se implementa un índice compuesto en la base de datos para las consultas del catálogo y una capa de caché en memoria con Redis (TTL de 30 segundos), descartando el escalamiento vertical o migración a microservicios en esta fase.

## Consecuencias y Evidencia
- **Positivo:** La simulación M/G/c demuestra que el p95 baja drásticamente de 16.8 s a 122 ms con 16 req/s.
- **Trade-off:** Requiere gestión de invalidación y tolera una eventual inconsistencia de inventario de hasta 30 s.
