# Registro de Revisión Cruzada entre Pares — Laboratorio 06 (Modelo C4)

Documentación de la revisión cruzada de arquitectura realizada mediante **GitHub Issues** entre los equipos:
* **Equipo Evaluador:** Grupo 06 — Plataforma AgroConecta
* **Equipo Evaluado:** Grupo 07 — San Camilo en Línea
* **Artefacto Evaluado:** Modelo C4 en Structurizr DSL (`workspace.dsl`), vistas exportadas y trazabilidad con ADRs.
* **Fecha de Sesión:** 19/10/2026

---

## 1. Issue de Evaluación Recibida (GitHub Issue #12)

**Título:** `[Revisión Cruzada C4] Auditoría de Arquitectura Grupo 07 (San Camilo en Línea)`  
**Autor:** `@agroconecta-lead` (Grupo 06)  

### Contenido del Issue:

> ### Lista de Cotejo Oficial C4 Aplicada:
> 
> | Criterio de Verificación | Cumple (Sí/No) | Observaciones del Grupo 06 |
> |---|:---:|---|
> | **1. Nivel 1 - Contexto:** ¿Se identifican claramente las personas, el sistema central y los sistemas externos fuera de control? | **Sí** | Se definen Cliente, Comerciante y Repartidor, con límites claros hacia Yape y WhatsApp Business API. |
> | **2. Nivel 2 - Contenedores:** ¿Cada contenedor representa una unidad ejecutable o almacén de datos con tecnología y protocolo explícitos? | **Sí** | PWA en React, API en Django REST, PostgreSQL 16, Celery Worker y Redis 7 con protocolos HTTPS, SQL y Redis claramente definidos. |
> | **3. Nivel 3 - Componentes:** ¿Los componentes del API reflejan `paquetes.puml` y forman un grafo acíclico? | **Sí** | 5 componentes mapeados. La relación es estrictamente unidireccional: `pedidos -> catalogo/pagos/notificaciones/entregas`. |
> | **4. Nivel 4 - Dinámica:** ¿Se modela el flujo crítico con pasos numerados coherentes con la máquina de estados? | **Sí** | Flujo de 7 pasos que garantiza persistencia transaccional antes del encolamiento de WhatsApp. |
> | **5. Despliegue:** ¿El entorno de producción es coherente con las restricciones de infraestructura (R-03)? | **Sí** | Todo el backend se aloja en un único servidor VPS con Nginx y Docker Compose. |
> 
> ### Preguntas y Observaciones de Mejora del Grupo 06:
> 1. **Consulta sobre persistencia de pedidos vs WhatsApp:** *¿Qué ocurre si la API de WhatsApp está caída al momento de ejecutar el paso 6 de la vista dinámica?*
> 2. **Exportación de artefactos:** *En la carpeta `export/` de la etiqueta inicial solo se visualizaba el contexto en Mermaid. Se requiere contar con los 5 diagramas exportados en `.mmd`, `.puml` y archivos PNG para renderizado estático.*
> 3. **Aislamiento de la Pasarela:** *¿Por qué el componente de pagos no gestiona la lógica de reintentos en caso de timeout del proveedor Yape?*

---

## 2. Respuesta Fundamentada del Grupo 07 y Acciones de Corrección

**Respondido por:** `@knndy18` y `@diego-pari` (Grupo 07)  
**Fecha:** 20/10/2026  

### Respuestas Técnicas y Evidencias en el Repositorio:

1. **Sobre la resiliencia ante caídas de WhatsApp (`QA-02`):**
   * *Explicación:* En el paso 4 del flujo dinámico (`ConfirmacionPago`), el pedido global cambia a estado `PAGADO` y se persiste en PostgreSQL de forma síncrona dentro de una transacción ACID. El paso 5 y 6 delegan la notificación a `compNotificaciones`, el cual no realiza llamadas HTTP directas sino que inserta un mensaje en la cola Redis (`enqueue`).
   * *Garantía:* Si WhatsApp o Meta Cloud están caídos, la confirmación de la compra al cliente **no se bloquea ni se pierde** ($0$ pedidos perdidos). El `worker` Celery ejecuta reintentos exponenciales con jitter en segundo plano hasta que el servicio externo se restablezca.

2. **Sobre la exportación de las 5 vistas y carpeta de imágenes (`E6`):**
   * *Acción aplicada:* Se implementó la exportación completa de las 5 vistas en `docs/architecture/c4/export/`:
     - `structurizr-Contexto.puml` y `.mmd`
     - `structurizr-Contenedores.puml` y `.mmd`
     - `structurizr-Componentes.puml` y `.mmd`
     - `structurizr-ConfirmacionPago.puml` y `.mmd`
     - `structurizr-Despliegue-Produccion.puml` y `.mmd`
   * Se generaron las imágenes PNG renderizadas en `docs/architecture/c4/img/` (`Contexto.png`, `Contenedores.png`, `Componentes.png`, `ConfirmacionPago.png`, `Despliegue-Produccion.png`).

3. **Sobre el manejo de timeouts en la pasarela Yape (`QA-03`):**
   * *Acción aplicada:* En el diseño de bajo nivel (`src/pedidos/pagos.py`), los adaptadores `YapeAdapter` y `PlinAdapter` fueron reforzados con un bucle de reintento automático (hasta 3 intentos ante excepciones `TimeoutError` de red) antes de marcar la transacción como rechazada, garantizando tolerancia ante jitter en conexiones móviles 3G (`R-04`).

---

## 3. Evaluación Entregada al Grupo 06 (AgroConecta)

**Revisor:** Grupo 07  
**Resultado de la Evaluación a AgroConecta:**
* Cumplimiento del inventario de actores agrícolas y cooperativas.
* Diagrama de contenedores con separación adecuada de servicios de geolocalización.
* Se recomendó a AgroConecta documentar con mayor claridad el protocolo entre su app móvil offline-first y el backend central.
* **Calificación otorgada:** 19/20 (Aprobado con observaciones menores atendidas).
