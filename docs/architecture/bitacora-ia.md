# Bitácora de uso de IA – San Camilo en Línea

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|---|---|---|---|---|---|
| 1 | 03/10 | ChatGPT | Prompt 1 adaptado: 3 alternativas de estilo arquitectónico para MVP en 1 mes. | Microservicios + Kubernetes con arquitectura orientada a eventos para el catálogo y pedidos. | Excede R-01 (1 mes) y R-03 (presupuesto bajo para un único VPS). Violaba la capacidad operativa del equipo de 3 devs (R-02). | Rechazada |
| 2 | 03/10 | ChatGPT | Prompt 2: Crítica adversarial a la alternativa recomendada por la IA. | Monolito Modular como solución pragmática para cumplir con el plazo y el presupuesto. | Se verificó contra R-01, R-02, R-03 y QA-04. Se confirmó que mantiene límites de dominio sin sobrecosto operativo. | Aceptada |
| 3 | 03/10 | Gemini | Elección del motor de persistencia para el catálogo y pedidos multi-puesto. | MongoDB (NoSQL) para permitir esquemas flexibles en los productos de los puestos. | Se verificó contra R-07 (carrito multi-puesto) y R-06 (auditoría). Se requería integridad ACID para pedidos y pagos. Se cambió a PostgreSQL. | Corregida |
| 4 | 03/10 | ChatGPT | Redacción inicial del ADR-003 para Autenticación y Autorización por Rol. | Autenticación delegada 100 % en un proveedor externo de Identidad SaaS (Auth0). | Violaba R-03 (presupuesto bajo) y agregaba dependencia externa innecesaria. Se ajustó a autenticación propia con sesiones seguras y RBAC. | Corregida |
| 5 | 03/10 | Gemini | Estrategia de tolerancias a fallos para notificaciones de WhatsApp. | Bloquear la confirmación del pedido en la API hasta que la llamada HTTP a WhatsApp retorne 200 OK. | Violaba QA-02 (0 pedidos perdidos ante fallas externas). Se corrigió para desacoplar la notificacion mediante una cola de reintentos persistida. | Corregida |
| 6 | 17/10 | Antigravity (Gemini) | Lab 06 – E3: Modelado de componentes del API Backend en Structurizr DSL a partir de `paquetes.puml`. | 5 componentes (`compCatalogo`, `compPedidos`, `compPagos`, `compNotificaciones`, `compEntregas`) con descripciones, tecnologías y relaciones acíclicas. Vista `component` definida con `autolayout lr`. | Se verificó ausencia de ciclos: la dirección es unidireccional (Pedidos → Catálogo / Pagos / Notificaciones / Entregas). Se validó sintaxis DSL y coherencia de identificadores con E1/E2. Se confirmó que las relaciones componente → `sancamilo.db` y componente → `sancamilo.cola` son válidas con `!identifiers hierarchical`. | Aceptada con ajuste: se añadió `compEntregas` para cubrir el módulo del Repartidor (RF-07) presente en `paquetes.puml` pero omitido en los comentarios de ejemplo del `workspace.dsl` original. |
| 7 | 17/10 | Antigravity (Gemini) | Lab 06 – E4/E5: Vista dinámica del flujo de confirmación y pago Yape, y entorno de despliegue `Producción` en Structurizr DSL. | Vista `dynamic` con 7 pasos numerados basados fielmente en `secuencia-flujo.puml`; `deploymentEnvironment "Producción"` con nodos: Dispositivos de Usuario → Servidor VPS (Proxy Nginx + Docker Compose con contenedores API, Worker, Redis, PostgreSQL) y Servicios Externos (Yape, WhatsApp). | Se verificó que los `containerInstance` referencian identificadores definidos en E2. Se confirmó que `softwareSystemInstance` se usa correctamente para sistemas externos. Se revisó que el Worker de Celery aparece como `deploymentNode` independiente, coherente con el contenedor E2. Sintaxis validada manualmente contra la especificación Structurizr DSL v2. | Aceptada. **Decisión arquitectónica**: el entorno de producción usa un único VPS con Docker Compose (sin Kubernetes ni cloud PaaS) para cumplir R-03 (presupuesto bajo) y R-01 (plazo 1 mes), según ADR-001. |

---

## Anexo: Prompts

### Prompt 1 (Interacción 1)
> "Actúa como un arquitecto de software senior. Para la plataforma 'San Camilo en Línea' (MVP e-commerce para el Mercado San Camilo de Arequipa), necesitamos proponer 3 estilos arquitectónicos para evaluar en una matriz de decisión. Contexto y restricciones: plazo estricto de 1 mes (R-01), equipo de máximo 3 desarrolladores (R-02), presupuesto reducido para un único servidor VPS (R-03), comerciantes interactuando desde celulares de gama baja en red 3G (R-04, QA-01) y carritos con productos de múltiples puestos (R-07). Propón 3 alternativas, analiza pros y contras, y sugiere cuál deberíamos elegir."

### Prompt 2 (Interacción 2)
> "Aplica una crítica adversarial destructiva a la propuesta de usar Microservicios o arquitecturas distribuidas para San Camilo en Línea. Evalúa el impacto real de las transacciones distribuidas, latencia, costos de nube y esfuerzo de despliegue frente a las restricciones críticas de R-01 (1 mes de plazo), R-02 (equipo de 3 developers) y R-03 (un solo servidor VPS económicamente viable)."

### Prompt 3 (Interacción 3)
> "Propon un motor de base de datos para almacenar el catálogo de productos por puesto y los pedidos de los clientes en San Camilo en Línea. Compara brevemente PostgreSQL vs. MongoDB considerando que los comerciantes editan precios rápidamente pero las ventas deben conservarse para auditoría."

### Prompt 4 (Interacción 4)
> "Escribe un borrador de ADR en formato Nygard para la autenticación y roles de usuarios (cliente, comerciante, repartidor, administrador) en San Camilo en Línea. Sugiere el mecanismo más rápido de implementar."

### Prompt 5 (Interacción 5)
> "¿Como debemos manejar la integración de notificaciones por WhatsApp en el flujo de creación de un pedido para garantizar que una caida de la API de WhatsApp no afecte la venta?"

### Prompt 6 (Interacción 6 – Lab 06, E3)
> "Actúa como un Arquitecto de Software experto en el modelo C4 y en Structurizr DSL. Estoy desarrollando el Laboratorio 06 del proyecto 'San Camilo en Línea' bajo el enfoque de 'Arquitectura como Código'. Mi rol en el equipo (Integrante 2: Kennedy) consiste en desarrollar la Parte 2 del laboratorio (E3, E4 y E5). A partir del `workspace.dsl` actual (con E1+E2), `paquetes.puml`, `secuencia-flujo.puml`, `despliegue.puml` y `drivers.md`, genera: (E3) dentro del contenedor `api`, modela 4 o más componentes funcionales mapeados desde `paquetes.puml` con responsabilidad, tecnología y relaciones internas acíclicas; define la vista `component` correspondiente."

### Prompt 7 (Interacción 7 – Lab 06, E4/E5)
> "Continúa con los ejercicios E4 y E5. (E4) Define una vista `dynamic` para el flujo crítico de confirmación y pago de un pedido multi-puesto con Yape, reutilizando el escenario de `secuencia-flujo.puml` con al menos 4 pasos numerados. (E5) Define el `deploymentEnvironment 'Producción'` coherente con `despliegue.puml` y `drivers.md` (R-03), anidando correctamente los nodos de infraestructura (Dispositivo de usuario/Navegador PWA, Servidor VPS, Docker Compose con contenedores) y ubicando una `containerInstance` de cada contenedor E2 en su nodo correspondiente. Asegura sintaxis 100% válida para `./structurizr.sh validate -w workspace.dsl`."

