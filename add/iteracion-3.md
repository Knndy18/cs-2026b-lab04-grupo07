# Iteración 3 de ADD — Rendimiento [QA-04]
## San Camilo en Línea 2.0 — `add/iteracion-3.md`

**Responsable:** Kennedy Chirinos Rojas  
**Fecha:** 2026-10-31  
**Laboratorio:** 08 — Attribute-Driven Design

---

## 1. Objetivo de la Iteración

Resolver el escenario de rendimiento del Árbol de Utilidad (`docs/architecture/utilidad/arbol.md`):

> **[QA-04] Rendimiento (H,M):** Ante una ráfaga concurrente de **20 req/s** entre los 3 mercados (campaña de festividades), el sistema debe responder las lecturas del catálogo con un tiempo de respuesta **p95 ≤ 1 500 ms**, respondiendo desde la caché Redis con TTL = 30 s.

El punto de sensibilidad S1 del ATAM-lite (Diego) advierte que este SLA depende críticamente de mantener una tasa de aciertos (Hit Rate) de Redis por encima del **15%**.

---

## 2. Contexto Arquitectónico de Entrada

| Elemento | Valor | Fuente |
|---|---|---|
| Carga objetivo | 20 req/s — 3 mercados simultáneos | QA-04 / arbol.md |
| SLA | p95 ≤ 1 500 ms | QA-04 / arbol.md |
| Servidores disponibles | 4 workers gunicorn (VPS único) | R-03, ADR-001 |
| Caché disponible | Redis 7 (ya en workspace.dsl) | workspace.dsl |
| Sensibilidad S1 | Hit Rate Redis > 15% | atam-lite.md |
| Riesgo R3 | Caché fría post-reinicio → posible SLA excedido | atam-lite.md |
| Mitigación R3 | Índices compuestos `(mercado_id, estado, categoria)` | atam-lite.md |

---

## 3. Modelo Matemático — Cola M/M/c

El sistema de la API Backend con 4 workers se modela como una cola M/M/c:

- **Proceso de llegadas:** Poisson con tasa $\lambda = 20 \text{ req/s}$ (llegadas memoryless)
- **Proceso de servicio:** Exponencial con media $\mu_s$ [ms/req] por worker
- **Servidores:** $c = 4$ workers gunicorn

### Variables del modelo

$$\rho = \frac{\lambda}{c \cdot \mu} \qquad \text{(utilización por worker)}$$

$$a = \frac{\lambda}{\mu} \qquad \text{(tráfico ofrecido en Erlangs)}$$

### Fórmula de Erlang C — Probabilidad de espera

$$C(c, \rho) = \frac{\dfrac{a^c}{c!\,(1-\rho)}}{\displaystyle\sum_{k=0}^{c-1}\frac{a^k}{k!} + \dfrac{a^c}{c!\,(1-\rho)}}$$

### Tiempo medio de espera en cola

$$W_q = \frac{C(c, \rho)}{c\,\mu - \lambda} \qquad \text{[segundos]}$$

### Tiempo medio total en sistema

$$W = W_q + \frac{1}{\mu}$$

---

## 4. Evaluación de Tácticas Arquitectónicas

### Táctica 1 — Sin optimización (baseline) ❌ VIOLA SLA

**Parámetros del escenario ANTES:**
- $\mu_s = 145 \text{ ms}$ (cada solicitud → consulta directa a PostgreSQL)
- $\mu = 1000/145 = 6.90 \text{ req/s por worker}$
- $\rho = 20 / (4 \times 6.90) = 0.725$ → **72.5% de utilización**

**Resultado analítico M/M/c:**

| Variable | Valor |
|---|---|
| $C(c=4, \rho=0.725)$ | 0.4682 |
| $W_q$ (espera en cola) | 61.7 ms |
| $W$ (tiempo en sistema) | 206.7 ms |
| p95 analítico | ≈ 440 ms |

**Resultado de simulación discreta (`fitness/rendimiento.py`, N=50,000):**

| Percentil | Latencia |
|---|---|
| p50 | 162.2 ms |
| p90 | 461.1 ms |
| p95 | **579.5 ms** |
| p99 | 827.0 ms |
| Cumple SLA p95 ≤ 1500 ms | ✅ Cumple (pero sin margen) |

> **Nota:** Con $\lambda = 20$ req/s y $c = 4$ workers, el sistema sin caché cumple el SLA en condiciones normales pero con utilización del 72.5% — **sin margen de seguridad para picos**. Si $\lambda$ aumenta a 25 req/s (solo un 25%), $\rho$ sube a 0.906 y el sistema colapsa ($W_q \to \infty$ cuando $\rho \to 1$).

---

### Táctica 2 — Replicación de lectura PostgreSQL ❌ DESCARTADA

**Descripción:** Agregar una réplica de lectura de PostgreSQL (read replica) para distribuir las consultas de catálogo entre la instancia principal y la réplica.

**Razones de descarte:**

1. **Violación de R-03 (VPS único):** Una réplica de lectura requiere un servidor adicional o una solución cloud de replicación (ej. Amazon RDS Read Replica), incompatible con la restricción de VPS único de bajo costo.

2. **Latencia de replicación no determinista:** La replicación asíncrona de PostgreSQL introduce un lag de replicación variable (típicamente 10–500 ms). Para un catálogo de mercado que se actualiza con frecuencia (stocks, precios), las lecturas desde la réplica pueden devolver datos desactualizados durante el lag — lo que en el contexto multitenant podría cruzar datos entre mercados si la política RLS no se ha replicado aún.

3. **Complejidad innecesaria:** El análisis de la simulación demuestra que **Redis caché resuelve el problema con la infraestructura ya disponible** (Redis 7 ya existe en `workspace.dsl`). Agregar una réplica de lectura agrega complejidad operativa sin beneficio adicional.

4. **Evidencia cuantitativa:** La simulación con caché Redis reduce $\rho$ de 0.725 a **0.155**, dejando un margen de capacidad del 84.5% para absorber picos. La replicación habría reducido $\rho$ a ≈ 0.36 con 2 réplicas — inferior al margen alcanzado con caché.

---

### Táctica 3 — Caché Redis TTL=30 s con invalidación por mercado ✅ ELEGIDA

**Descripción:** Las lecturas del catálogo se sirven desde Redis con TTL = 30 s. La clave de caché incluye el `mercado_id` para garantizar el aislamiento multitenant: `catalogo:{mercado_id}:{categoria}:{pagina}`. Las escrituras (actualización de stock/precio) invalidan las claves del mercado afectado.

**Parámetros del escenario DESPUÉS:**
- Hit Rate = 82% (S1 del atam-lite: documentado como necesario > 15%; 82% es conservador para catálogo estático con TTL 30 s)
- $\mu_{\text{efectiva}} = 0.82 \times 6 + 0.18 \times 145 = 4.92 + 26.1 = 31.0 \text{ ms/req}$
- $\mu = 1000/31.0 = 32.26 \text{ req/s por worker}$
- $\rho = 20 / (4 \times 32.26) = 0.155$ → **15.5% de utilización**

**Resultado analítico M/M/c:**

| Variable | Valor |
|---|---|
| $C(c=4, \rho=0.155)$ | 0.003928 |
| $W_q$ (espera en cola) | **0.04 ms** |
| $W$ (tiempo en sistema) | **31.1 ms** |
| p95 analítico | ≈ 31.1 ms |

**Resultado de simulación discreta (`fitness/rendimiento.py`, N=50,000, semilla=43):**

| Percentil | Latencia |
|---|---|
| p50 | 21.5 ms |
| p90 | 71.4 ms |
| p95 | **92.9 ms** |
| p99 | 142.2 ms |
| Cumple SLA p95 ≤ 1 500 ms | **✅ CUMPLE** (margen: 93.8%) |

---

## 5. Tabla Comparativa de Trade-offs

| Criterio | Sin caché (baseline) | Réplica lectura (descartada) | Caché Redis (elegida) |
|---|---|---|---|
| p95 simulado | 579.5 ms | ~280 ms (estimado) | **92.9 ms** |
| Utilización ρ | 0.725 (72.5%) | ~0.36 | **0.155 (15.5%)** |
| Margen para picos | 27.5% antes de colapso | 64% | **84.5%** |
| Infraestructura adicional | Ninguna | +1 servidor / RDS | **Ninguna** (Redis ya existe) |
| Frescura de datos | 100% (tiempo real) | ~99% (lag repl.) | **96.7%** (TTL 30 s) |
| Violación R-03 | No | **Sí** | No |
| Cumple QA-04 p95 ≤ 1500 ms | ✅ (sin margen) | ✅ | **✅ (93.8% de margen)** |
| Costo operativo | Bajo | Alto | **Bajo** |

---

## 6. Evidencia Cuantitativa — Simulación M/M/c

### Resultados completos del script `fitness/rendimiento.py`

```
═════════════════════════════════════════════════════════════════
  RESUMEN COMPARATIVO
─────────────────────────────────────────────────────────────────
  Métrica                       ANTES      DESPUÉS     Mejora
  ────────────────────── ──────────── ──────────── ──────────
  p95 [ms]                      579.5         92.9      84.0%
  Media [ms]                    211.6         31.0      85.3%
  Utilización ρ                 0.725        0.155
  SLA p95≤1500ms              ✓ CUMPLE    ✓ CUMPLE
═════════════════════════════════════════════════════════════════
  Mejora p95: 579.5 ms → 92.9 ms  (84.0% reducción)
```

El gráfico generado se encuentra en [`fitness/rendimiento_resultados.png`](../fitness/rendimiento_resultados.png).

### Análisis de sensibilidad — Hit Rate de Redis

El punto de sensibilidad S1 del atam-lite documenta que el sistema necesita Hit Rate > 15%. La siguiente tabla muestra cómo varía el p95 en función del hit rate:

| Hit Rate Redis | $\mu_{\text{ef}}$ [ms] | $\rho$ | p95 estimado [ms] | Cumple SLA |
|---|---|---|---|---|
| 0% (sin caché) | 145.0 | 0.725 | 579 | ✅ (sin margen) |
| 15% (mínimo S1) | 124.7 | 0.623 | 358 | ✅ |
| 50% | 75.5 | 0.378 | 111 | ✅ |
| 82% (objetivo) | 31.0 | **0.155** | **93** | ✅ |
| 95% | 12.5 | 0.063 | 13 | ✅ |

**Conclusión:** Incluso en el peor caso documentado por S1 (Hit Rate = 15%), el sistema cumple el SLA con p95 ≈ 358 ms — muy por debajo del límite de 1 500 ms. El Outbox Pattern de la Iteración 2 no introduce latencia adicional en las lecturas del catálogo.

---

## 7. Componentes Arquitectónicos Instanciados

```
Módulo Catálogo (compCatalogo — workspace.dsl)
  └─ CatalogoService.listar_productos(mercado_id, categoria, pagina)
       1. Construir clave: f"catalogo:{mercado_id}:{categoria}:{pagina}"
       2. cache_hit = redis.get(clave)
       3. Si cache_hit: retornar inmediatamente [~6 ms]
       4. Si cache_miss:
          a. consultar PostgreSQL con RLS activo [~145 ms]
          b. redis.setex(clave, ttl=30, value=resultado_serializado)
          c. retornar resultado
       
       Invalidación (escrituras del comerciante):
       5. ProductoService.actualizar_producto():
          a. UPDATE productos SET ...
          b. redis.delete(f"catalogo:{mercado_id}:*")  [pattern delete]

Cola Redis 7 (container cola — workspace.dsl)
  └─ Namespace caché catálogo: catalogo:{mercado_id}:{categoria}:{pagina}
  └─ TTL: 30 segundos (trade-off T1 — atam-lite.md)
  └─ Política de evicción: allkeys-lru (evitar OOM en VPS)
```

---

## 8. Riesgo R3 y su Mitigación (atam-lite.md)

El riesgo R3 documenta que tras un reinicio de Redis, la caché está vacía y las primeras solicitudes impactan directamente PostgreSQL. La mitigación propuesta por Diego es:

> **Índices compuestos en PostgreSQL:** `CREATE INDEX idx_productos_mercado_estado_cat ON productos (mercado_id, estado, categoria)`.

Con estos índices, el tiempo de consulta sin caché cae de 145 ms a ≈ 65 ms, lo que eleva el SLA sin caché a:
- $\mu = 1000/65 = 15.38$ req/s por worker
- $\rho = 20/(4 \times 15.38) = 0.325$ → p95 ≈ 82 ms (caché fría)

El riesgo de violar el SLA durante caché fría queda así eliminado.

---

## 9. Trade-offs Documentados

| Ganancia | Costo |
|---|---|
| p95 de 579.5 ms → 92.9 ms (**-84%**) | Datos del catálogo con hasta 30 s de lag (T1) |
| Utilización de 72.5% → 15.5% | Implementar invalidación de caché en escrituras |
| Margen de absorción de picos del 84.5% | Gestión del TTL y política de evicción Redis |
| Usa infraestructura ya disponible | Monitoreo del hit rate (alertar si < 15%) |

---

## 10. Conexión con otros Entregables

| Entregable | Vinculación |
|---|---|
| `docs/architecture/utilidad/arbol.md` (Diego E1) | QA-04 (H,M) es el driver de esta iteración |
| `docs/architecture/atam-lite.md` (Diego E3) | S1, T1 y R3 documentan la sensibilidad al hit rate |
| `fitness/rendimiento.py` (Kennedy) | Script que genera la evidencia M/M/c |
| `fitness/rendimiento_resultados.png` (Kennedy) | Gráfico Antes vs. Después |
| `add/iteracion-2.md` (Kennedy E4) | Iteración anterior — QA-03 Disponibilidad |
| `docs/architecture/c4/workspace.dsl` (Kennedy Lab 06) | Redis 7 y API Backend ya modelados |
