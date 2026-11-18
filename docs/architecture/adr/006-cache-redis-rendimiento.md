# ADR-006: Adopción de Caché Redis para Catálogo y Control de Latencia

- Estado: Aceptado
- Fecha: 2026-10-28
- Decisores: Kennedy, Diego y Nagin (Grupo 07)
- Escenario Atendido: `QA-04` (Rendimiento: Ráfaga de $20\text{ req/s}$ con $p95 \le 1.5\text{ s}$)
- Iteración ADD: Iteración 1 (Rendimiento)

## Contexto

Con la expansión de la plataforma hacia los mercados Altiplano y Río Seco, el volumen de consultas concurrentes al catálogo general en horas pico se estima en $\lambda = 20\text{ peticiones/segundo}$. 
En la arquitectura base sin caché, cada lectura al catálogo ejecuta consultas SQL relacionales que implican joins entre tablas de puestos, categorías y productos, con una latencia media de base de datos de $45\text{ ms}$. Bajo una ráfaga sostenida, esto saturaría los $c=4$ workers de Gunicorn en el servidor VPS único (`R-03`), elevando la utilización de CPU por encima del $80\%$ y degradando el tiempo de respuesta percentil 95 por encima de los $1.8\text{ segundos}$, violando el límite contractual de $p95 \le 1.5\text{ s}$ (`QA-04`).

## Alternativas consideradas

1. **Escalado Vertical del VPS o Réplicas de Lectura de PostgreSQL:** Aumentar CPU/RAM del servidor o crear réplicas de lectura.
   * *Descarte:* Viola la restricción presupuestal `R-03` (un solo VPS económico) y no resuelve el cuello de botella de E/S en disco para datos idénticos de alta consulta.
2. **Caché en Memoria Local del Proceso Django (LocMemCache):** Guardar productos en la memoria de cada worker.
   * *Descarte:* Genera inconsistencia entre workers independientes de Gunicorn y sobrecarga la memoria RAM de los procesos de aplicación.
3. **Caché Centralizada en Redis 7 con expiración TTL de 30 segundos (Táctica: Mantener Múltiples Copias):**
   * *Ventajas:* Latencia de lectura sub-milisegundo ($2\text{ ms}$), contenedor ya presente en el entorno Docker Compose para Celery, y tasa de aciertos estimada del $60\%$ para productos populares.

## Decisión

Adoptar una **Caché Distribuida en Redis 7** con estrategia *Cache-Aside* y tiempo de vida (*Time-To-Live - TTL*) de 30 segundos para las consultas al catálogo general y listados de productos por mercado.

La decisión está respaldada por la simulación matemática de teoría de colas $M/M/c$ con modelo Erlang C (`fitness/rendimiento.py`), la cual arrojó:
- **Tiempo de respuesta medio ($W$):** $27.4\text{ ms}$ (reducción del $62\%$ frente a los $72.1\text{ ms}$ sin caché).
- **Percentil 95 ($p95$):** **$72.4\text{ ms}$**, cumpliendo holgadamente con el presupuesto de $p95 \le 1,500\text{ ms}$.
- **Utilización del servidor ($\rho$):** Se redujo del $45\%$ al **$17\%$**, liberando capacidad para procesamiento transaccional de pedidos.

## Consecuencias

* **Positivas:** Reducción drástica de la latencia observada por los clientes móviles en redes 3G (`R-04`), absorción de picos de tráfico en días festivos y nulo incremento en costo de infraestructura (`R-03`).
* **Negativas / Trade-off:** Introduce consistencia eventual en el catálogo (`T1`). Si un comerciante cambia el precio o agota el stock de un producto, los compradores podrían ver el dato previo durante un máximo de 30 segundos.
* **Mitigación:** Al momento de agregar al carrito (`RF-02`) y confirmar el pedido (`RF-03`), el módulo de pedidos realiza una validación transaccional directa contra PostgreSQL (`SELECT FOR UPDATE`), garantizando que jamás se confirme un ítem sin stock real.

## Plan de evolución y monitoreo

Se implementa la Fitness Function automatizada `fitness/rendimiento.py` en el pipeline de CI/CD para verificar en cada pull request que el $p95$ simulado se mantenga estrictamente por debajo de $1,500\text{ ms}$.
