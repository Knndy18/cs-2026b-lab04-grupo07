# ADR-008: Aislamiento Multitenant con Row-Level Security en PostgreSQL

- Estado: Aceptado
- Fecha: 2026-10-30
- Decisores: Kennedy, Diego y Nagin (Grupo 07)
- Escenarios Atendidos: `QA-01` (Modificabilidad: nuevo mercado $\le 1$ día) y `QA-02` (Seguridad: 0 filtraciones entre mercados)
- Iteración ADD: Iteración 3 (Modificabilidad y Aislamiento Multitenant)

## Contexto

Para la fase 2.0, el modelo de negocio se expande del Mercado San Camilo a dos nuevos mercados de Arequipa: **Mercado Altiplano** y **Mercado Río Seco**. Cada mercado opera con comerciantes independientes, catálogos propios, tarifas de delivery diferenciadas y reglas de comisión particulares.
Se requiere soportar esta arquitectura *Multitenant* garantizando dos requerimientos críticos:
1. **Modificabilidad (`QA-01`):** Capacidad de incorporar un nuevo mercado en $\le 1$ día sin tener que alterar el código fuente del núcleo de la aplicación.
2. **Seguridad y Aislamiento de Datos (`QA-02`):** Garantía estricta de que un comerciante o cliente de un mercado no pueda bajo ninguna circunstancia leer o modificar productos, pedidos o comprobantes de otro mercado (**0 filtraciones**).
3. **Restricción de Infraestructura (`R-03`):** Toda la solución debe coexistir en el único servidor VPS asignado, sin incurrir en costos de bases de datos adicionales.

## Alternativas consideradas

1. **Bases de Datos Físicas Independientes por Mercado (Database-per-Tenant):** Crear una base de datos PostgreSQL por cada mercado.
   * *Descarte:* Multiplica el consumo de memoria RAM en el VPS por cada nuevo mercado (violando `R-03`), complica las migraciones de esquema en CI/CD y excede el tiempo límite de entrega de 1 mes (`R-01`).
2. **Esquemas Separados en la Misma Base de Datos (Schema-per-Tenant):** Un esquema SQL (`sancamilo`, `altiplano`, `rioseco`) dentro de la misma base de datos.
   * *Descarte:* Requiere lógica de enrutamiento dinámico compleja en Django ORM y mantenimiento de múltiples migraciones paralelas, aumentando el riesgo de errores operativos.
3. **Esquema Compartido con Columna Discriminadora (`mercado_id`) y Row-Level Security (RLS) en PostgreSQL 16 (Táctica: Restringir Acceso y Esquema Común):**
   * *Ventajas:* Un solo esquema relacional optimizado, soporte nativo a nivel de motor de base de datos (`ALTER TABLE ... ENABLE ROW LEVEL SECURITY`), sobrecarga de rendimiento imperceptible ($\approx 2\%$) y nulo consumo adicional de memoria en el VPS.

## Decisión

Adoptar un **Esquema Compartido con Row-Level Security (RLS) en PostgreSQL 16**:

1. Todas las tablas de dominio (`puestos`, `productos`, `pedidos`, `pagos`) incluyen la clave foránea `mercado_id UUID NOT NULL`.
2. Se habilitan políticas de seguridad a nivel de fila directamente en PostgreSQL:
   ```sql
   ALTER TABLE productos ENABLE ROW LEVEL SECURITY;
   CREATE POLICY tenant_isolation_policy ON productos
       FOR ALL
       USING (mercado_id = NULLIF(current_setting('app.current_market_id', true), '')::uuid);
   ```
3. Un middleware en Django extrae de forma automática el identificador del mercado desde el token JWT criptográfico del usuario y lo inyecta en la sesión de base de datos (`SET LOCAL app.current_market_id = ...`) al inicio de cada petición HTTP.
4. Para dar de alta un nuevo mercado (`QA-01`), basta con insertar una fila en la tabla de configuración `mercados` con sus comisiones y polígonos de entrega, completándose en **menos de 1 hora** sin modificar el código fuente.

## Consecuencias

* **Positivas:** Cumplimiento simultáneo de `QA-01` (nuevo mercado en $\le 1$ día) y `QA-02` (aislamiento garantizado por el motor de base de datos con **0 filas filtradas**).
* **Positivas:** Máxima eficiencia en el uso de memoria RAM en el servidor VPS único (`R-03`).
* **Negativas / Sensibilidad:** Se genera el punto de sensibilidad `S2`: el aislamiento depende críticamente de que el middleware inyecte siempre el `mercado_id` correcto y de que no se omitan directivas RLS en nuevas tablas.
* **Mitigación:** Se implementa una Fitness Function de Seguridad en el pipeline de CI/CD que ejecuta consultas cruzadas automatizadas con tokens de prueba y verifica que el resultado sea siempre vacío.

## Plan de evolución y monitoreo

Se implementa una prueba de integración continua en GitHub Actions (`tests/test_rls_security.py`) que valida automáticamente las políticas RLS en cada migración de base de datos.
