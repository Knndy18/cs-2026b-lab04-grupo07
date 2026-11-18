# Bitácora de Interacciones con Inteligencia Artificial — Laboratorio 06 (Modelo C4)

Registro exhaustivo de las interacciones con herramientas de inteligencia artificial utilizadas durante el diseño, modelado, validación y exportación de la arquitectura del sistema **San Camilo en Línea** utilizando el **Modelo C4** y **Structurizr DSL** (Arquitectura como Código).

**Sistema:** San Camilo en Línea (Plataforma e-commerce MVP para el Mercado San Camilo de Arequipa)  
**Herramientas:** Antigravity (Gemini 1.5 Pro / Claude Sonnet 3.5)  
**Marco de Referencia:** C4 Model (Simon Brown) & Structurizr DSL v2  

---

## Tabla Resumen de Interacciones

| # | Fecha | Entregable | Prompt (Resumen) | Propuesta de la IA | Verificación y Crítica Humana | Decisión |
|---|---|---|---|---|---|---|
| **1** | 15/10/2026 | E1 – Contexto | Modelado del Nivel 1 en Structurizr DSL a partir de `drivers.md`. | Propuso personas (Cliente, Comerciante, Repartidor), sistema central y sistemas externos (Yape, WhatsApp). | Verificado contra los actores de `drivers.md` y restricciones R-04 y R-05. Relaciones bidireccionales corregidas. | **Aceptada con corrección** |
| **2** | 16/10/2026 | E2 – Contenedores | Definición de contenedores ejecutables y almacenes de datos (Nivel 2). | Sugirió 6 contenedores incluyendo microservicios independientes para pagos y catálogo. | **Rechazada:** Violaba el `ADR-001` (Monolito Modular) y la restricción presupuestal `R-03` (VPS único). Se unificó en contenedor API Django + PWA + DB + Celery + Redis. | **Corregida** |
| **3** | 17/10/2026 | E3 – Componentes | Descomposición del contenedor API en componentes a partir de `paquetes.puml`. | Generó 4 componentes iniciales (`compCatalogo`, `compPedidos`, `compPagos`, `compNotificaciones`). Omitió `compEntregas`. | El equipo detectó que faltaba el módulo de Entregas (RF-07). Además, la IA propuso una dependencia de `notificaciones` hacia `pedidos` que generaba un ciclo. | **Corregida:** Se añadió `compEntregas` y se forzó grafo estrictamente acíclico. |
| **4** | 17/10/2026 | E4 – Dinámica | Modelado de la vista dinámica del flujo crítico de pago multipuesto con Yape. | Propuso un flujo de 10 pasos con llamadas sincrónicas bloqueantes hacia WhatsApp y pasarela. | Violaba `QA-02` (0 pedidos perdidos ante fallos externos). Se corrigió para que el guardado en base de datos sea previo al encolado asíncrono en Redis/Celery (7 pasos alineados a `secuencia-flujo.puml`). | **Corregida** |
| **5** | 17/10/2026 | E5 – Despliegue | Modelado del entorno `deploymentEnvironment "Producción"` en Structurizr DSL. | Propuso clúster Kubernetes administrado en AWS EKS con balanceador ALB. | **Rechazada:** Desalineada con `R-03` (presupuesto bajo para 1 VPS) y `R-01` (1 mes). Se adaptó a un único nodo VPS con Nginx y Docker Compose mapeando cada `containerInstance`. | **Corregida** |
| **6** | 18/10/2026 | E6 – Validación y CLI | Validación sintáctica `./structurizr.sh validate` y exportación a PlantUML y Mermaid. | Sugirió introducir Apache Kafka como broker de eventos para pasar la validación de mensajería empresarial. | **Falso Positivo Rechazado:** Structurizr DSL valida consistencia de relaciones sin exigir middleware pesado. Se mantuvo Redis 7 y se exportaron las 5 vistas completas. | **Aceptada con verificación** |

---

## Detalle de Interacciones

### Interacción 1 — Nivel 1: Contexto del Sistema (E1)
* **Fecha:** 15/10/2026
* **Herramienta:** Gemini 1.5 Pro
* **Prompt enviado:**
  > "Actúa como arquitecto de software. A partir del documento `drivers.md` del caso 'San Camilo en Línea' (e-commerce para comerciantes del mercado de Arequipa, pago único con Yape/Plin, confirmaciones por WhatsApp y repartidores locales), genera la sección `model` y la vista `systemContext` en Structurizr DSL. Identifica los actores humanos, el sistema central y los sistemas externos fuera de nuestro control."
* **Propuesta de la IA:** Declaró las personas `cliente`, `comerciante`, `repartidor`, el sistema `sancamilo`, y los sistemas externos `pasarela` (Proveedor de Pagos) y `whatsapp` (WhatsApp Business API).
* **Evaluación del Equipo:**
  - Los límites del sistema fueron adecuadamente identificados.
  - La IA inicialmente conectó `cliente -> pasarela` de forma directa; se corrigió para que la interacción de pago fluya a través de `sancamilo` para registro de la referencia o constancia (`RF-04`).
* **Decisión:** Aceptada con corrección en la cardinalidad y flujo de la relación de pago.

---

### Interacción 2 — Nivel 2: Contenedores y Protocolos (E2)
* **Fecha:** 16/10/2026
* **Herramienta:** Claude Sonnet 3.5
* **Prompt enviado:**
  > "Basándote en el ADR-001 (Monolito Modular) y la restricción R-03 (un único servidor VPS de bajo costo), descompón el sistema San Camilo en Línea en sus Contenedores C4 dentro de Structurizr DSL. Especifica tecnología y protocolo de comunicación en cada relación. La PWA debe ser liviana (R-04)."
* **Propuesta de la IA:** La IA sugirió una arquitectura basada en microservicios independientes (`catalogo-service`, `orders-service`, `payments-service`) desplegados en contenedores separados con gRPC.
* **Evaluación del Equipo:**
  - **Falsa buena práctica:** La IA propuso microservicios como el 'estándar moderno', ignorando las restricciones explícitas de `R-01` (1 mes de plazo), `R-02` (equipo de 3 desarrolladores) y `R-03` (un solo servidor VPS).
  - El equipo refutó la propuesta exigiendo fidelidad estricta al `ADR-001`.
* **Decisión:** Rechazada y corregida. Se estructuró en 5 contenedores lógicos coherentes:
  1. `pwa` (React + Service Workers) en navegador web.
  2. `api` (Python / Django REST Framework) como monolito modular.
  3. `db` (PostgreSQL 16) para persistencia relacional ACID.
  4. `cola` (Redis 7) para colas y caché de catálogo.
  5. `worker` (Celery) para tareas de fondo y reintentos.

---

### Interacción 3 — Nivel 3: Componentes del API Backend (E3)
* **Fecha:** 17/10/2026
* **Herramienta:** Gemini 1.5 Pro
* **Prompt enviado:**
  > "Diseña los componentes internos del contenedor `api` en Structurizr DSL a partir de `docs/design/paquetes.puml`. Demuestra que el grafo de dependencias entre componentes es estrictamente acíclico. Mapea responsabilidades y tecnologías para cada componente."
* **Propuesta de la IA:** Declaró 4 componentes: `compCatalogo`, `compPedidos`, `compPagos`, `compNotificaciones`. Sugirió una dependencia donde `compNotificaciones` consultaba directamente a `compPedidos` para verificar el estado de los pedidos.
* **Evaluación del Equipo:**
  - **Detección de Ciclo:** Si `compPedidos` invoca a `compNotificaciones` para encolar avisos, y `compNotificaciones` consulta a `compPedidos`, se genera un ciclo bidireccional (`pedidos <-> notificaciones`), violando la regla C4 de diseño.
  - **Omisión funcional:** Omitió el módulo de entregas del repartidor (`RF-07`).
* **Decisión:** Corregida. Se incorporó `compEntregas` y se estableció una relación unidireccional estricta donde `compPedidos` es el orquestador hacia Catálogo, Pagos, Notificaciones y Entregas.

---

### Interacción 4 — Flujo Dinámico: Confirmación y Pago Multi-Puesto (E4)
* **Fecha:** 17/10/2026
* **Herramienta:** Claude Sonnet 3.5
* **Prompt enviado:**
  > "Genera una vista `dynamic sancamilo.api 'ConfirmacionPago'` en Structurizr DSL que modele fielmente el escenario crítico de `docs/design/secuencia-flujo.puml`: confirmación y pago de pedido multi-puesto con Yape en 7 pasos numerados, garantizando persistencia segura."
* **Propuesta de la IA:** La IA entregó un flujo donde el paso 3 era el envío inmediato del mensaje a WhatsApp por HTTP síncrono antes de guardar en la base de datos.
* **Evaluación del Equipo:**
  - **Fallo de Disponibilidad:** Si la API de WhatsApp presenta latencia o caída temporal, la confirmación de la venta se bloquearía o fallaría, perdiendo el pedido del cliente (violación directa de `QA-02`).
  - Se corrigió el orden: primero se verifica el pago, luego se guarda en PostgreSQL con estado `PAGADO`, luego se encola el mensaje de manera asíncrona en Redis, y finalmente se retorna `200 OK` al cliente.
* **Decisión:** Aceptada tras reordenar los 7 pasos conforme a la máquina de estados y `secuencia-flujo.puml`.

---

### Interacción 5 — Entorno de Despliegue Producción (E5)
* **Fecha:** 17/10/2026
* **Herramienta:** Gemini 1.5 Pro
* **Prompt enviado:**
  > "Modela en Structurizr DSL el `deploymentEnvironment 'Producción'`. Considera que por R-03 contamos con un único VPS en la nube (Ubuntu 22.04 LTS), Nginx como proxy inverso y Docker Compose para orquestar los contenedores. Ubica las instancias de los 5 contenedores de E2 en sus nodos de ejecución respectivos."
* **Propuesta de la IA:** Generó el bloque `deploymentEnvironment` estructurado en:
  - Dispositivos de Usuario (Navegador Web con `pwaInstance`).
  - Servidor VPS (Nginx + Docker Compose conteniendo `apiInstance`, `workerInstance`, `colaInstance`, `dbInstance`).
  - Servicios Externos (`pasarelaInstance` y `whatsappInstance`).
* **Evaluación del Equipo:**
  - La anidación de nodos refleja con exactitud la infraestructura física y virtualizada del proyecto.
  - Se verificó que todas las instancias referencian identificadores válidos definidos en la sección `model`.
* **Decisión:** Aceptada sin objeciones.

---

### Interacción 6 — Validación con Structurizr CLI y Falsos Positivos (E6)
* **Fecha:** 18/10/2026
* **Herramienta:** Claude Sonnet 3.5
* **Prompt enviado:**
  > "Revisa el archivo `workspace.dsl` consolidado contra la lista de chequeo de la Guía de Laboratorio 06. ¿Existe alguna advertencia de sintaxis o inconsistencia al ejecutar `structurizr validate` y qué vistas deben exportarse a PlantUML y Mermaid?"
* **Propuesta de la IA:** Afirmó que para una arquitectura de e-commerce real, Structurizr advertía la falta de un bus de eventos persistente tipo Kafka y recomendó agregarlo al modelo.
* **Evaluación del Equipo:**
  - **Falso Positivo de la IA:** Structurizr DSL valida relaciones jerárquicas y consistencia de identificadores, no impone brokers específicos de mensajería empresarial. Incorporar Kafka violaría la restricción de memoria RAM del VPS único (`R-03`).
  - Se verificó la sintaxis DSL directamente. Todas las vistas (`Contexto`, `Contenedores`, `Componentes`, `ConfirmacionPago`, `Despliegue-Produccion`) exportan limpiamente a PlantUML (`.puml`) y Mermaid (`.mmd`).
* **Decisión:** Se descartó la sugerencia de Kafka y se completó la exportación de las 5 vistas y generación de imágenes PNG en `docs/architecture/c4/img/`.
