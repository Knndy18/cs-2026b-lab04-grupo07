# Árbol de Utilidad y Escenarios de Calidad – San Camilo en Línea 2.0 (`E1`)

## 1. Contexto de Crecimiento
Con la expansión hacia los mercados **Altiplano** y **Río Seco**, el sistema debe soportar una arquitectura *Multitenant*, manteniendo un estricto aislamiento de datos entre comerciantes y la capacidad de integrar reglas específicas por mercado en un plazo no mayor a 1 mes (`R-01`) y sobre un único servidor VPS (`R-03`).

---

## 2. Escenarios Medibles de Calidad

### `QA-01`: Modificabilidad (Incorporación de Mercados) – **Prioridad: (H, H)**
- **Fuente:** Equipo de administración de San Camilo en Línea.
- **Estímulo:** Solicitud de incorporación del Mercado Altiplano con reglas de comisión y delivery propias.
- **Artefacto:** Módulo de Catálogo y Configuración de Mercados.
- **Entorno:** Operación normal del sistema.
- **Respuesta:** Configurar la entidad del mercado, catálogo y tarifas de delivery mediante metadatos y esquemas dinámicos.
- **Medida:** Despliegue completado en $\le 1$ día sin modificar el código fuente del núcleo (`ADR-008`).

### `QA-02`: Seguridad / Aislamiento Multitenant – **Prioridad: (H, M)**
- **Fuente:** Comerciante malintencionado o error de consulta del cliente.
- **Estímulo:** Intento de consulta o modificación directa a productos o ventas pertenecientes a otro mercado.
- **Artefacto:** API REST y Base de Datos PostgreSQL con políticas RLS (Row-Level Security).
- **Entorno:** Operación concurrente con múltiples tenants.
- **Respuesta:** Filtrar automáticamente las consultas asignando la clave de sesión `mercado_id` desde el token JWT.
- **Medida:** 0 filtraciones de datos entre comerciantes de distintos mercados (estrictamente 0 filas retornadas).

### `QA-03`: Disponibilidad (Resiliencia en Pagos) – **Prioridad: (H, H)**
- **Fuente:** Servicio externo (Proveedor Yape/Plin).
- **Estímulo:** Caída total de la pasarela de pagos durante 20 minutos en hora pico de ventas.
- **Artefacto:** Módulo de Pagos, Circuit Breaker y Tabla Transaccional Outbox.
- **Entorno:** Pico de ventas en los 3 mercados.
- **Respuesta:** Abrir el circuito (*Fail Fast*), evitar la caída de la API, persistir la transacción en la tabla `outbox` en PostgreSQL y procesarla asíncronamente con Celery al recuperar conexión.
- **Medida:** 0 pedidos perdidos y $100\%$ de transacciones procesadas tras el restablecimiento del servicio (`ADR-007`).

### `QA-04`: Rendimiento (Capacidad Bajo Carga) – **Prioridad: (H, M)**
- **Fuente:** Clientes finales de los tres mercados simultáneos.
- **Estímulo:** Ráfaga concurrente de $20\text{ req/s}$ buscando ofertas en el catálogo general.
- **Artefacto:** API Monolito Modular y Caché Redis.
- **Entorno:** Campaña festiva o fines de semana.
- **Respuesta:** Responder las lecturas del catálogo desde la caché en Redis con TTL de 30 segundos.
- **Medida:** Tiempo de respuesta percentil 95 $p95 \le 1.5\text{ segundos}$ ($72.4\text{ ms}$ en simulación $M/M/c$, `ADR-006`).

### `QA-05`: Modificabilidad (Nuevo Medio de Pago) – **Prioridad: (M, L)**
- **Fuente:** Product Owner / Administración de pagos.
- **Estímulo:** Solicitud de incorporar una nueva pasarela (ej. Plin v2 o tarjeta de débito).
- **Artefacto:** Módulo de Pagos (`pagos.py`) y Fábrica de Pasarelas.
- **Entorno:** Mantenimiento evolutivo del sistema.
- **Respuesta:** Crear un nuevo adaptador que implemente `PasarelaPago` y registrarlo en `FabricaPasarelas`.
- **Medida:** Cambio implementado en $\le 2$ días-persona y con 0 cambios en el código de pedidos (`ADR-005`).

### `QA-06`: Seguridad (Cifrado de Datos en Tránsito y Reposo) – **Prioridad: (M, L)**
- **Fuente:** Agente malicioso en la red o acceso no autorizado a disco.
- **Estímulo:** Intento de interceptación de tráfico o extracción de credenciales/comprobantes de pago.
- **Artefacto:** Nginx (TLS 1.3), PostgreSQL y almacenamiento del servidor VPS.
- **Entorno:** Operación en red pública de Internet.
- **Respuesta:** Terminar TLS en Nginx y cifrar particiones de persistencia en reposo.
- **Medida:** $100\%$ del tráfico forzado a HTTPS (puerto 443) y claves privadas protegidas fuera de repositorios (`R-08`).

---

## 3. Matriz de Priorización de Escenarios

| Importancia \ Dificultad | Alta Dificultad (H) | Media Dificultad (M) | Baja Dificultad (L) |
|:---:|:---:|:---:|:---:|
| **Alta Importancia (H)** | **`QA-01`** (Nuevo mercado $\le 1$ día)<br>**`QA-03`** (Caída Yape $\rightarrow$ 0 perdidos) | **`QA-02`** (0 filtraciones RLS)<br>**`QA-04`** (Ráfaga $20\text{ req/s} \rightarrow p95 \le 1.5\text{ s}$) | — |
| **Media Importancia (M)** | — | — | **`QA-05`** (Medio pago $\le 2$ días)<br>**`QA-06`** (Cifrado HTTPS y reposo) |
| **Baja Importancia (L)** | — | — | — |

---

## 4. Justificación de Corrección sobre la IA
- **Propuesta Inicial de la IA:** Calificar el cifrado de datos (`QA-06`) como `(H, H)`.
- **Corrección Fundamentada del Equipo:** Se corrigió a **`(M, L)`** porque el cifrado TLS en Nginx y el cifrado de disco en el servidor VPS ya se encontraban resueltos desde los laboratorios previos mediante configuraciones estándar de infraestructura, sin requerir esfuerzo de diseño arquitectónico complejo durante la expansión multitenant.
