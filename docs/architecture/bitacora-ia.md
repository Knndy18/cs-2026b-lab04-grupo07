# Bitácora de uso de IA – San Camilo en Línea

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|---|---|---|---|---|---|
| 1 | 03/10 | ChatGPT | Prompt 1 adaptado: 3 alternativas de estilo arquitectónico para MVP en 1 mes. | Microservicios + Kubernetes con arquitectura orientada a eventos para el catálogo y pedidos. | Excede R-01 (1 mes) y R-03 (presupuesto bajo para un único VPS). Violaba la capacidad operativa del equipo de 3 devs (R-02). | Rechazada |
| 2 | 03/10 | ChatGPT | Prompt 2: Crítica adversarial a la alternativa recomendada por la IA. | Monolito Modular como solución pragmática para cumplir con el plazo y el presupuesto. | Se verificó contra R-01, R-02, R-03 y QA-04. Se confirmó que mantiene límites de dominio sin sobrecosto operativo. | Aceptada |
| 3 | 03/10 | Gemini | Elección del motor de persistencia para el catálogo y pedidos multi-puesto. | MongoDB (NoSQL) para permitir esquemas flexibles en los productos de los puestos. | Se verificó contra R-07 (carrito multi-puesto) y R-06 (auditoría). Se requería integridad ACID para pedidos y pagos. Se cambió a PostgreSQL. | Corregida |
| 4 | 03/10 | ChatGPT | Redacción inicial del ADR-003 para Autenticación y Autorización por Rol. | Autenticación delegada 100 % en un proveedor externo de Identidad SaaS (Auth0). | Violaba R-03 (presupuesto bajo) y agregaba dependencia externa innecesaria. Se ajustó a autenticación propia con sesiones seguras y RBAC. | Corregida |
| 5 | 03/10 | Gemini | Estrategia de tolerancias a fallos para notificaciones de WhatsApp. | Bloquear la confirmación del pedido en la API hasta que la llamada HTTP a WhatsApp retorne 200 OK. | Violaba QA-02 (0 pedidos perdidos ante fallas externas). Se corrigió para desacoplar la notificacion mediante una cola de reintentos persistida. | Corregida |

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
