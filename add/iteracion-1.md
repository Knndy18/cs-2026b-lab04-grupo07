# Iteración 1 de ADD — Modificabilidad [QA-01]
## San Camilo en Línea 2.0 — `add/iteracion-1.md`

**Responsable:** Kennedy Chirinos Rojas  
**Fecha:** 2026-10-31  
**Laboratorio:** 08 — Attribute-Driven Design

---

## 1. Objetivo de la Iteración

Resolver el escenario de calidad crítico de mayor prioridad en el Árbol de Utilidad elaborado por Diego (`docs/architecture/utilidad/arbol.md`):

> **[QA-01] Modificabilidad (H,H):** Ante una solicitud de incorporar el Mercado Altiplano con sus propias reglas de comisión, el equipo de administración debe poder desplegar la nueva entidad de mercado, catálogo y tarifas de delivery **en ≤ 1 día sin modificar el código fuente del núcleo**.

La arquitectura actual (Monolito Modular, `ADR-001`) fue diseñada para un único mercado (San Camilo). La expansión a tres mercados (Altiplano y Río Seco) requiere una decisión arquitectónica explícita sobre cómo manejar la variabilidad entre tenants sin violar los límites de los módulos existentes.

---

## 2. Contexto Arquitectónico de Entrada

| Elemento | Valor | Fuente |
|---|---|---|
| Estilo arquitectónico | Monolito Modular (Python/Django) | ADR-001 |
| Stack de persistencia | PostgreSQL 16 | ADR-002 |
| Infraestructura | VPS único — Docker Compose | R-03 |
| Sensibilidad identificada | S2: aislamiento depende de `mercado_id` en JWT | atam-lite.md |
| Trade-off identificado | T1: caché Redis vs. frescura de stock | atam-lite.md |
| Restricción de plazo | MVP en 1 mes, equipo de 3 devs | R-01, R-02 |
| Módulos afectados | Catálogo, Pedidos, Pagos, Notificaciones, Entregas | workspace.dsl |

---

## 3. Evaluación de Tácticas Arquitectónicas

Se evaluaron tres tácticas para habilitar la incorporación de nuevos mercados sin modificar el núcleo:

### Táctica 1 — Config-Driven Multitenancy con tabla `mercados` ✅ ELEGIDA

**Descripción:** Añadir una entidad `Mercado` en la base de datos con atributos configurables (nombre, comisión, tarifas de delivery, reglas de horario). El `mercado_id` se inyecta en cada solicitud vía JWT y se propaga hacia PostgreSQL mediante Row-Level Security (RLS) para filtrar automáticamente los datos de cada tenant.

**Cambios arquitectónicos necesarios:**
- Nueva tabla `mercados` con columnas: `id`, `nombre`, `comision_pct`, `tarifas_delivery` (JSONB), `activo`.
- Middleware Django que extrae `mercado_id` del JWT y ejecuta `SET app.current_mercado_id`.
- Políticas RLS en tablas `productos`, `pedidos`, `pagos`.
- **0 cambios** en los módulos de negocio (Catálogo, Pedidos, Pagos).

**Módulos tocados para agregar un nuevo mercado:**

| Artefacto | Acción | ¿Modifica código fuente núcleo? |
|---|---|---|
| `migrations/0010_add_mercado.py` | Migración nueva | No — nueva migración |
| `INSERT INTO mercados (...)` | Inserción de datos | No — solo datos |
| JWT issuer config | Ajuste de configuración | No — archivo `.env` |
| RLS policy (una vez creada) | Sin cambio posterior | — |

**Costo estimado:** 0.5 días-persona para el primer mercado; 0.1 días-persona para el segundo en adelante.  
**Cumplimiento QA-01:** ✅ ≤ 1 día sin tocar código fuente del núcleo.

---

### Táctica 2 — Módulos de Plugin por Mercado (evaluada)

**Descripción:** Cada mercado se implementa como un módulo Python independiente con sus propias reglas de negocio, que se carga dinámicamente al iniciar la aplicación mediante un sistema de plugins (similar a `django-plugins` o `pluggy`).

**Análisis:**
- Permite máximo aislamiento de reglas por mercado.
- Requiere definir e implementar un sistema de puntos de extensión (hooks) en cada módulo: Catálogo, Pedidos, Pagos.
- Para 3 mercados con reglas simples (solo tarifas y comisiones diferentes), el overhead de implementar el sistema de plugins supera el beneficio en el plazo del MVP.

**Costo estimado:** 5–7 días-persona para implementar la infraestructura de plugins.  
**Cumplimiento QA-01:** ⚠️ Viable a largo plazo, pero excede el plazo para el MVP.

---

### Táctica 3 — Base de Datos Independiente por Mercado ❌ DESCARTADA

**Descripción:** Cada mercado opera sobre su propia instancia de PostgreSQL, garantizando aislamiento físico total de los datos.

**Razones de descarte (argumentadas técnica y arquitectónicamente):**

1. **Violación directa de R-03 (Presupuesto):** El VPS único de bajo costo tiene recursos limitados de RAM y CPU. Tres instancias PostgreSQL 16 consumirían un mínimo de 600 MB de RAM base cada una (shared_buffers mínimos), lo que suma 1.8 GB solo para las bases de datos, dejando recursos insuficientes para la API, Redis y Celery.

2. **Violación de R-01 (Plazo) y R-02 (Equipo):** Gestionar tres pipelines de migración independientes (`python manage.py migrate --database=altiplano`) requiere configurar `DATABASE_ROUTERS` en Django, mantener 3 esquemas de migración sincronizados y triplicar los scripts de backup — inviable para un equipo de 3 personas en 1 mes.

3. **Complejidad operativa desproporcionada:** Consultas que agreguen datos de los 3 mercados (reportes del administrador) requerirían joins entre bases de datos distintas, lo que en PostgreSQL necesita extensiones como `postgres_fdw` (Foreign Data Wrappers), agregando una dependencia de infraestructura no justificada para el MVP.

4. **Evidencia del ATAM-lite (Diego):** El análisis NR1 confirma que el Monolito Modular con 4 workers opera a 35% de utilización de CPU, demostrando que el aislamiento físico de DB no es necesario para la carga proyectada. La respuesta fundamentada del equipo al evaluador adversario en `atam-lite.md` documenta que RLS introduce únicamente un sobrecosto de rendimiento del **2%** — estadísticamente insignificante.

**Conclusión del descarte:** La táctica de base de datos por mercado viola R-01, R-02 y R-03 simultáneamente sin aportar beneficios medibles para la escala actual. Queda descartada con posibilidad de reevaluación únicamente si el número de mercados supera 10 y los requisitos regulatorios de aislamiento físico se vuelven mandatorios.

---

## 4. Decisión Arquitectónica

**Táctica seleccionada:** Config-Driven Multitenancy con tabla `mercados` + Row-Level Security en PostgreSQL.

**Justificación cuantificada:**

| Criterio | Táctica 1 (elegida) | Táctica 2 (plugins) | Táctica 3 (descartada) |
|---|---|---|---|
| Días-persona para nuevo mercado | **0.5** | 5–7 (infra) + 0.5 | N/A — excede capacidad |
| Módulos del núcleo modificados | **0** | 3–5 (hooks) | 0 (pero 3 DB configs) |
| Cumple R-03 (VPS único) | **✅** | ✅ | ❌ |
| Cumple R-01 (1 mes) | **✅** | ⚠️ | ❌ |
| Cumple QA-01 (≤ 1 día) | **✅** | ⚠️ | ❌ |
| Riesgo R1 (RLS defectuosa) | Mitigado por FF-04 | Bajo (aislamiento código) | Ninguno (aislamiento físico) |

---

## 5. Evidencia Cuantitativa — Modificabilidad

La táctica elegida garantiza que incorporar un nuevo mercado toca **0 líneas de código fuente del núcleo**. La evidencia se mide contando los artefactos modificados:

### Baseline — Sin arquitectura Multitenant (estado inicial)

Con el sistema original de un solo mercado, incorporar "San Camilo II" requería:

| Artefacto a modificar | Tipo de cambio | Impacto |
|---|---|---|
| `views.py` en Catálogo | Condicional `if mercado == 'altiplano'` | Modifica código núcleo |
| `serializers.py` en Pedidos | Reglas de tarifa hardcodeadas | Modifica código núcleo |
| `services.py` en Pagos | Comisión diferente por if/elif | Modifica código núcleo |
| `settings.py` | Nueva constante de configuración | Modifica configuración |

**Total artefactos del núcleo modificados:** 3 archivos de código + tests asociados.

### Después — Con Config-Driven Multitenancy

| Artefacto a modificar | Tipo de cambio | ¿Toca el núcleo? |
|---|---|---|
| `INSERT INTO mercados VALUES (...)` | Solo datos en BD | ❌ No |
| `0010_add_mercado_altiplano.py` | Migración nueva | ❌ No |
| `.env` (JWT config) | Variable de entorno | ❌ No |

**Total artefactos del núcleo modificados: 0.**

### Métricas de acoplamiento — antes vs. después

| Métrica | Antes | Después | Delta |
|---|---|---|---|
| Archivos del núcleo modificados por mercado | 3 | **0** | **-100%** |
| Tiempo estimado por mercado nuevo | 2–3 días-persona | **0.5 días-persona** | **-80%** |
| Riesgo de regresión en módulos existentes | Alto (editar código) | **Ninguno** (solo datos) | **Eliminado** |
| Cumplimiento QA-01 (≤ 1 día) | ❌ No cumple | **✅ Cumple** | — |

---

## 6. Componentes Arquitectónicos Instanciados

```
Módulo Catálogo
  └─ Middleware: TenantMiddleware
       • Extrae mercado_id del JWT (claim: "mercado_id")
       • Ejecuta: SET app.current_mercado_id = %s
       • Se aplica a todas las solicitudes autenticadas

Base de Datos PostgreSQL 16
  └─ Tabla: mercados
       • id UUID PRIMARY KEY
       • nombre VARCHAR(100)
       • comision_pct DECIMAL(5,2)
       • tarifas_delivery JSONB
       • activo BOOLEAN
  └─ RLS activado en: productos, pedidos, pagos, entregas
       • POLICY: USING (mercado_id = current_setting('app.current_mercado_id')::uuid)
```

---

## 7. Trade-offs Identificados

- **Ganancia:** Modificabilidad extrema — 0 cambios en código fuente para incorporar nuevos mercados.
- **Costo:** La correcta extracción del `mercado_id` en el middleware es crítica (S2 — atam-lite.md). Una política RLS omitida expone los datos entre mercados (R1 — riesgo crítico).
- **Mitigación:** Fitness Function de seguridad `FF-04` (documentada por Nagin en CI): prueba automatizada que verifica que una consulta con token de Mercado A devuelve **0 filas** del Mercado B.

---

## 8. Conexión con otros Entregables

| Entregable | Vinculación |
|---|---|
| `docs/architecture/utilidad/arbol.md` (Diego E1) | QA-01 (H,H) es el driver de esta iteración |
| `docs/architecture/atam-lite.md` (Diego E3) | S2 y R1 documentan el riesgo de RLS |
| `docs/design/patrones/metricas.md` (Diego E6) | Metodología de medición de artefactos modificados |
| `.github/workflows/fitness.yml` (Nagin E5) | FF-04 valida el aislamiento RLS en CI |
| `add/iteracion-2.md` (Kennedy E4) | Continúa con QA-03 Disponibilidad |
