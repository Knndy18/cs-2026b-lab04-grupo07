# Árbol de Utilidad y Escenarios de Calidad – San Camilo en Línea 2.0 (`E1`)

## 1. Contexto de Crecimiento
Con la expansión hacia los mercados **Altiplano** y **Río Seco**, el sistema debe soportar arquitectura *Multitenant*, manteniendo un estricto aislamiento de datos entre comerciantes y la capacidad de integrar reglas específicas por mercado en un plazo no mayor a 1 mes.

---

## 2. Escenarios Medibles de Calidad

### `QA-01`: Modificabilidad (Incorporación de Mercados) – **Prioridad: (H, H)**
- **Fuente:** Equipo de administración de San Camilo en Línea.
- **Estímulo:** Solicitud de incorporación del Mercado Altiplano con reglas de comisión propias.
- **Artefacto:** Módulo de Catálogo y Configuración de Mercados.
- **Entorno:** Operación normal del sistema.
- **Respuesta:** Configurar la entidad del mercado, catálogo y tarifas de delivery.
- **Medida:** Despliegue completado en $\le 1$ día sin modificar el código fuente del núcleo.

### `QA-02`: Seguridad / Aislamiento Multitenant – **Prioridad: (H, M)**
- **Fuente:** Comerciante malintencionado o error de consulta del cliente.
- **Estímulo:** Intento de consulta directa a productos o ventas pertenecientes a otro mercado.
- **Artefacto:** API REST y Base de Datos PostgreSQL con políticas RLS (Row-Level Security).
- **Entorno:** Operación concurrente con múltiples tenants.
- **Respuesta:** Filtrar automáticamente las consultas asignando la clave `mercado_id` desde el JWT.
- **Medida:** 0 filtraciones de datos entre comerciantes de distintos mercados (0 filas retornadas).

### `QA-03`: Disponibilidad (Resiliencia en Pagos) – **Prioridad: (H, H)**
- **Fuente:** Servicio externo (Proveedor Yape/Plin).
- **Estímulo:** Caída total de la pasarela de pagos durante 20 minutos en hora pico.
- **Artefacto:** Módulo de Pagos, Circuit Breaker y Tabla Outbox.
- **Entorno:** Pico de ventas en los 3 mercados.
- **Respuesta:** Abrir el circuito, evitar la caída de la API, encolar las solicitudes en la tabla `outbox` en PostgreSQL y procesarlas asíncronamente al recuperar conexión.
- **Medida:** 0 pedidos perdidos y $100\%$ de transacciones procesadas tras el restablecimiento del servicio.

### `QA-04`: Rendimiento (Capacidad Bajo Carga) – **Prioridad: (H, M)**
- **Fuente:** Clientes finales de los tres mercados.
- **Estímulo:** Ráfaga concurrente de $20\text{ req/s}$ buscando ofertas en el catálogo general.
- **Artefacto:** API Monolito Modular y Caché Redis.
- **Entorno:** Campaña de festividades o fines de semana.
- **Respuesta:** Responder las lecturas del catálogo desde la caché en Redis con TTL de 30s.
- **Medida:** Tiempo de respuesta $p95 \le 1.5\text{ segundos}$.

---

## 3. Justificación de Corrección sobre la IA
- **Propuesta de la IA:** Calificar el cifrado de datos (`QA-06`) como `(H, H)`.
- **Corrección del Equipo:** Se bajó a **`(M, L)`** porque el cifrado HTTPS y el cifrado de disco en el VPS único ya se encuentran implementados desde los laboratorios anteriores y su complejidad no aumenta con la llegada de los nuevos mercados.
