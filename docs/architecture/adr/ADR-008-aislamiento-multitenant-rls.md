# ADR-008: Aislamiento Multitenencia mediante Row-Level Security (RLS)

## Estado
Aceptado

## Contexto
Al incorporar nuevos puestos y comerciantes (QA-04), se debe garantizar estricto aislamiento de pedidos y reportes financieros sin incurrir en costos operativos de bases de datos independientes.

## Decisión
Se utiliza una base de datos unificada particionada lógicamente mediante discriminador de puesto (`tenant_id`), aplicando Row-Level Security (RLS) en PostgreSQL y propagación de claims en el token JWT.

## Consecuencias y Evidencia
- **Positivo:** Rápida incorporación de nuevas entidades sin despliegues de infraestructura ni migraciones complejas.
- **Trade-off:** Requiere pruebas estrictas y fitness functions para evitar fugas de datos ante mala configuración de políticas RLS.
