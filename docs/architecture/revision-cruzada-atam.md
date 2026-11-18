# Registro de Issue de Evaluación Cruzada ATAM-lite (Laboratorio 08)

Documentación del **GitHub Issue #15** correspondiente a la sesión de evaluación cruzada entre pares del Laboratorio 08.

* **Repositorio Evaluado:** `cs-2026b-lab04-grupo07` (San Camilo en Línea 2.0)
* **Equipo Evaluador:** Grupo 06 (`@agroconecta-lead`, `@agroconecta-dev`)
* **Equipo Evaluado:** Grupo 07 (`@knndy18`, `@diego-pari`, `@nagin-dev`)
* **Fecha:** 29 de octubre de 2026

---

## 1. Contenido del Issue Aperturado por el Grupo 06

**Título:** `[ATAM-lite Cruzado] Evaluación de Arquitectura San Camilo en Línea 2.0 — Grupo 06`

> ### Resumen de la Auditoría Arquitectónica:
> 
> Hemos revisado el Árbol de Utilidad (`arbol.md` y `arbol.dot`), las tres iteraciones de diseño ADD (`iteracion-1.md`, `iteracion-2.md`, `iteracion-3.md`), las simulaciones cuantitativas (`fitness/`) y los ADRs asociados (ADR-006 a ADR-008).
> 
> ### Matriz de Evaluación ATAM-lite:
> 
> | Atributo / Escenario | Táctica Evaluada | Veredicto Grupo 06 | Comentario / Riesgo Detectado |
> |---|---|:---:|---|
> | **`QA-01` (Modificabilidad)** | Metadatos y Esquema Compartido | **Aprobado** | Buena abstracción para incorporar Altiplano y Río Seco sin desplegar nuevo código. |
> | **`QA-02` (Seguridad / RLS)** | Row-Level Security en PostgreSQL | **Riesgo `R1`** | Dependencia crítica de la inyección de `mercado_id` en JWT. Exigimos prueba en CI. |
> | **`QA-03` (Disponibilidad)** | Transaccional Outbox + Celery | **Aprobado** | Simulación Monte Carlo sólida con 0 pedidos perdidos demostrados. |
> | **`QA-04` (Rendimiento)** | Caché Redis con TTL 30s | **Sensibilidad `S1`** | Dependiente del Hit Rate. Si cae al 0%, el p95 bordea el límite. |
> | **Infraestructura (`R-03`)** | Servidor VPS Único | **Riesgo `R2`** | El nodo único representa un punto único de falla (SPOF) para los 3 mercados. |
> 
> ### Conclusión del Grupo 06:
> La arquitectura presenta una fundamentación matemática y cuantitativa sobresaliente. Las compensaciones de consistencia eventual (`T1` y `T2`) están adecuadamente identificadas y mitigadas.

---

## 2. Respuestas y Cierre del Issue por el Grupo 07

> **Respuesta de `@knndy18` (Grupo 07):**
> 
> Agradecemos la rigurosa revisión del Grupo 06. Procedemos a documentar las acciones de cierre:
> 1. **Sobre el Riesgo `R1` (RLS):** Implementamos una Fitness Function automatizada en GitHub Actions (`.github/workflows/fitness.yml`) que verifica en cada build que una consulta con token del Mercado A no devuelva ninguna fila del Mercado B.
> 2. **Sobre el Punto de Sensibilidad `S1` (Hit Rate de Caché):** Agregamos índices compuestos `(mercado_id, categoria, estado)` en PostgreSQL para que en caso de caché fría tras reinicio de Redis, el p95 se mantenga en $\le 1.8\text{ s}$ sin colapso de la base de datos.
> 3. **Sobre el Riesgo `R2` (SPOF del VPS):** Documentamos formalmente en `atam-lite.md` y `ADR-001` la aceptación justificada del riesgo para el MVP de 1 mes (`R-01`), respaldado por backups automatizados fuera del servidor.
> 
> **Estado del Issue:** Cerrado como Completado y Aprobado.
