# Iteración 2 de ADD — Disponibilidad [QA-03]
## San Camilo en Línea 2.0 — `add/iteracion-2.md`

**Responsable:** Kennedy Chirinos Rojas  
**Fecha:** 2026-10-31  
**Laboratorio:** 08 — Attribute-Driven Design

---

## 1. Objetivo de la Iteración

Resolver el segundo escenario de calidad crítico del Árbol de Utilidad (`docs/architecture/utilidad/arbol.md`):

> **[QA-03] Disponibilidad (H,H):** Ante una caída total de la pasarela Yape/Plin durante **20 minutos** en hora pico, el sistema debe garantizar **0 pedidos perdidos** y el **100%** de las transacciones debe procesarse tras el restablecimiento del servicio.

El riesgo T2 del ATAM-lite (Diego) advierte el trade-off: garantizar disponibilidad implica aceptar **consistencia eventual** — el cliente no recibe confirmación en tiempo real, sino dentro de un tiempo máximo tolerable.

---

## 2. Contexto Arquitectónico de Entrada

| Elemento | Valor | Fuente |
|---|---|---|
| Módulo afectado | Pagos + Worker Celery | workspace.dsl |
| Riesgo identificado | R2: VPS único como SPOF | atam-lite.md |
| Trade-off identificado | T2: Outbox vs. confirmación en tiempo real | atam-lite.md |
| Cola de tareas disponible | Redis 7 + Celery Worker | workspace.dsl |
| Ventana de falla modelada | 20 min — P(falla) ≈ 15% del tráfico pico | QA-03 / arbol.md |
| SLA pedidos perdidos | 0 de N | QA-03 |

---

## 3. Evaluación de Tácticas Arquitectónicas

### Táctica A — Llamada directa sin resiliencia ❌ BASELINE (viola QA-03)

**Descripción:** El módulo Pedidos llama síncronamente a la pasarela Yape/Plin. Si la pasarela no responde, el pedido falla y se pierde.

**Resultado de la simulación (`fitness/disponibilidad.py`):**

| Métrica | Valor |
|---|---|
| Pedidos perdidos (N=10,000) | **1,550 (15.50%)** |
| Recuperados de la ventana de falla | 0.0% |
| Tiempo p95 de proceso | 2.87 min |
| Cumple QA-03 (0 perdidos) | **✗ VIOLA** |

**Veredicto:** Inaceptable. Pierde 1 de cada 6.5 pedidos durante una falla de 20 minutos.

---

### Táctica B — Reintentos con Backoff Exponencial (evaluada, insuficiente)

**Descripción:** Ante un timeout de Yape/Plin, el módulo reintenta la llamada hasta 3 veces con espera exponencial ($2^i \times 30$ segundos, $i = 1, 2, 3$).

**Análisis matemático de la ventana cubierta:**

$$t_{\text{max\_cubierto}} = \sum_{i=1}^{3} 2^i \times 30 = 60 + 120 + 240 = 420 \text{ s} = 7 \text{ min}$$

Un pedido que llegue cuando quedan más de 7 minutos de falla **no puede ser recuperado** con solo 3 reintentos. Dado que la caída dura 20 minutos, un pedido que llega al inicio de la ventana tiene tiempo residual de hasta 20 minutos — muy superior a los 7 minutos cubiertos.

**Resultado de la simulación (`fitness/disponibilidad.py`):**

| Métrica | Valor |
|---|---|
| Pedidos perdidos (N=10,000) | **1,000 (10.00%)** |
| Recuperados de la ventana de falla | 34.3% |
| Tiempo p95 de proceso | 3.60 min |
| Cumple QA-03 (0 perdidos) | **✗ VIOLA** |

**Veredicto:** Mejora el baseline un 35.5%, pero sigue perdiendo 1,000 pedidos. Insuficiente para QA-03.

---

### Táctica C — Outbox Pattern + Worker Asíncrono ✅ ELEGIDA

**Descripción:** El módulo Pedidos persiste el pedido inmediatamente en PostgreSQL con estado `PENDIENTE_PAGO` y registra la transacción pendiente en una tabla `outbox`. Un worker Celery monitorea la tabla y reintenta el cobro al detectar que el proveedor está disponible. Este patrón es el trade-off T2 documentado por Diego en `atam-lite.md`.

**Garantía formal:** El pedido **siempre** se persiste en la base de datos antes de intentar el cobro. La falla del proveedor de pagos **nunca** impide la persistencia del pedido.

**Modelo matemático — Probabilidad de pérdida con Outbox:**

Sea $F$ = evento "falla del proveedor durante la solicitud":

$$P(\text{pedido perdido} \mid \text{Outbox}) = P(\text{falla de PostgreSQL}) \approx 0$$

(PostgreSQL en el mismo VPS tiene disponibilidad ≥ 99.9% — R2 documenta el riesgo residual de SPOF del VPS como aceptado en el MVP.)

**Resultado de la simulación (`fitness/disponibilidad.py`, N=10,000, semilla=2028):**

| Métrica | Valor |
|---|---|
| Pedidos perdidos | **0 (0.00%)** |
| Recuperados de la ventana de falla | **100.0%** |
| Tiempo medio de proceso | 3.03 min |
| Tiempo p95 de proceso | **14.94 min** |
| Cumple QA-03 (0 perdidos) | **✓ CUMPLE** |
| Cumple tiempo ≤ 15 min | **✓ CUMPLE** |

---

## 4. Tabla Comparativa de Trade-offs

| Criterio | A — Sin resiliencia | B — Reintentos | C — Outbox (elegida) |
|---|---|---|---|
| Pedidos perdidos / 10,000 | **1,550** | **1,000** | **0** |
| Tasa de pérdida | 15.50% | 10.00% | **0.00%** |
| Recuperación de fallas | 0.0% | 34.3% | **100.0%** |
| Tiempo p95 confirmación | 2.87 min | 3.60 min | **14.94 min** |
| Confirmación en tiempo real | ✅ Sí | ✅ Sí | ⚠️ No (eventual) |
| Complejidad de implementación | Baja | Baja | Media |
| Cumple QA-03 | ❌ | ❌ | **✅** |
| Infraestructura adicional | Ninguna | Ninguna | Celery+Redis (ya existe) |

**Análisis del trade-off T2 (atam-lite.md):** El Outbox Pattern introduce consistencia eventual — el cliente espera hasta 14.94 min (p95) para recibir la confirmación final del pago. Este es el costo explícito de garantizar 0 pedidos perdidos. Para el contexto del Mercado San Camilo (compras de productos de mercado, no transacciones financieras críticas), este tiempo es aceptable y está dentro del SLA de ≤ 15 min.

---

## 5. Evidencia Cuantitativa — Simulación Monte Carlo

### Parámetros del modelo

| Parámetro | Valor | Justificación |
|---|---|---|
| $N$ (pedidos simulados) | 10,000 | Convergencia estadística (error estándar < 0.5%) |
| $P(\text{falla})$ | 0.15 | Caída 20 min en hora pico de 2h → 15% del tráfico |
| Duración máx. falla | 20 min | QA-03 / arbol.md |
| $t_{\text{worker}}$ Outbox | $\text{Uniforme}(0.1, 3.0)$ min | Celery poll interval = 10 s |
| Semilla aleatoria | 2026, 2027, 2028 | Una por estrategia — reproducible |

### Resultados numéricos de la simulación

```
═════════════════════════════════════════════════════════════════
  TABLA COMPARATIVA — fitness/disponibilidad.py
─────────────────────────────────────────────────────────────────
  Estrategia                          Perdidos  p95 [min]   QA-03
  ─────────────────────────────────── ──────── ────────── ───────
  A — Sin resiliencia (baseline)         1,550       2.87       ✗
  B — Reintentos backoff exp.            1,000       3.60       ✗
  C — Outbox Pattern (elegida)               0      14.94       ✓
═════════════════════════════════════════════════════════════════
```

El gráfico generado se encuentra en [`fitness/disponibilidad_resultados.png`](../fitness/disponibilidad_resultados.png).

---

## 6. Componentes Arquitectónicos Instanciados

```
Módulo Pagos (compPagos — workspace.dsl)
  └─ ServicioPagos.registrar_pago_pendiente()
       1. BEGIN TRANSACTION
       2. INSERT INTO pedidos (estado='PENDIENTE_PAGO', ...)  → persiste el pedido
       3. INSERT INTO outbox (tipo='COBRO_YAPE', payload, creado_en)
       4. COMMIT
       5. Retornar HTTP 202 Accepted + pedido_id al cliente

Worker Celery (container worker — workspace.dsl)
  └─ ProcesarOutboxTask (poll cada 10 s)
       1. SELECT * FROM outbox WHERE procesado=FALSE ORDER BY creado_en
       2. Para cada registro:
          a. Intentar cobro en Yape/Plin (YapeAdapter.cobrar())
          b. Si éxito: UPDATE pedidos SET estado='PAGADO'; UPDATE outbox SET procesado=TRUE
          c. Si falla: exponential backoff — próximo intento en 2^n × 10 s
       3. Notificar al comerciante vía WhatsApp (enqueue en Cola Redis)

Cola Redis 7 (container cola — workspace.dsl)
  └─ Queue: outbox_procesamiento  (prioridad alta)
  └─ Queue: notificaciones_whatsapp
```

---

## 7. Trade-offs Documentados

| Ganancia | Costo |
|---|---|
| 0 pedidos perdidos — QA-03 cumplido | Confirmación diferida (consistencia eventual) |
| Resiliencia ante fallas de 20 min | Cliente espera p95 = 14.94 min para confirmación |
| Usa infraestructura ya existente (Celery + Redis) | Implementar tabla `outbox` y task Celery |
| Auditoría completa de todos los intentos de cobro | Mayor complejidad de monitoreo del worker |

---

## 8. Conexión con otros Entregables

| Entregable | Vinculación |
|---|---|
| `docs/architecture/utilidad/arbol.md` (Diego E1) | QA-03 (H,H) es el driver de esta iteración |
| `docs/architecture/atam-lite.md` (Diego E3) | T2 documenta el trade-off Outbox vs. tiempo real |
| `fitness/disponibilidad.py` (Kennedy) | Script que genera la evidencia Monte Carlo |
| `fitness/disponibilidad_resultados.png` (Kennedy) | Gráfico Antes vs. Después |
| `add/iteracion-1.md` (Kennedy E2) | Iteración anterior — QA-01 Modificabilidad |
| `add/iteracion-3.md` (Kennedy E4) | Continúa con QA-04 Rendimiento |
