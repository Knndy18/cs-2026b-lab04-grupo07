# Bitácora de Interacciones con Inteligencia Artificial — Laboratorio 07 (Patrones de Diseño)

Registro completo de las interacciones con asistentes de IA durante la refactorización a patrones de diseño GoF, diseño de la capa de IA con guardrails, cálculo de métricas de complejidad con `radon` y suite de pruebas unitarias en `pytest`.

**Sistema:** San Camilo en Línea — Módulo de Pedidos y Pasarela de Pagos  
**Herramientas:** Antigravity (Claude Sonnet 3.5 / Gemini 1.5 Pro)  
**Marco Teórico:** Gang of Four (GoF), Refactoring to Patterns (Kerievsky), Clean Code (Martin)  

---

## Resumen de Interacciones

| # | Fecha | Entregable | Prompt (Resumen) | Propuesta de la IA | Verificación y Crítica del Equipo | Decisión |
|---|---|---|---|---|---|---|
| **1** | 20/10/2026 | E1 – Olores | Detección de *code smells* en `antes/servicio.py`. | Identificó método largo (CC=14), condicionales complejos y acoplamiento directo a Yape. | Confirmado con `radon cc`. Se priorizaron los olores de violación OCP y falta de resiliencia. | **Aceptada** |
| **2** | 21/10/2026 | E2 – Strategy/Adapter | Diseño de `pagos.py` con Strategy, Adapter y Factory. | Propuso interfaz abstracta `PasarelaPago`, adaptadores concretos (`YapeAdapter`, `PlinAdapter`) y fábrica. | Se verificó que los adaptadores manejasen `TimeoutError` con reintentos y que la fábrica no fuera Singleton. | **Aceptada con ajuste** |
| **3** | 22/10/2026 | E3 – State | Implementación del ciclo de vida de pedidos con patrón State (`estados.py`). | Sugirió jerarquía `EstadoPedido` (Borrador, Confirmado, Pagado, Cancelado) sustituyendo `if/elif`. | Se validó que las transiciones inválidas lancen excepciones específicas de dominio (`TransicionInvalidaError`). | **Aceptada** |
| **4** | 23/10/2026 | E4 – Observer | Notificaciones asíncronas con patrón Observer (`eventos.py`). | Propuso `PublicadorEventos` y suscriptores para WhatsApp y Logística. | Se verificó que un error en el envío de mensajes a WhatsApp no aborte la transacción de persistencia del pedido. | **Aceptada con ajuste** |
| **5** | 24/10/2026 | E5 – Capa de IA | Diseño de `ia.py` con Strategy (proveedores), Decorator (caché) y Chain of Responsibility (guardrails). | Generó arquitectura aislada con 5 validadores de entrada y 3 de salida para evitar alucinaciones e inyecciones. | Se agregó `GuardrailPreciosValidos` específico para moneda peruana (S/) y mitigación de alucinación de precios S/ 0.00. | **Aceptada con extensión** |
| **6** | 25/10/2026 | E6 – Métricas | Análisis de métricas con `radon` y evaluación de patrones rechazados. | Sugirió aplicar `Abstract Factory` y `Singleton` para "mayor elegancia". | **Rechazada (Patternitis):** Se rechazó Singleton por introducir estado mutable y Abstract Factory por carecer de familias de objetos. | **Rechazo Fundamentado** |

---

## Detalle de Interacciones

### Interacción 1 — Análisis de Olores de Código y Pruebas de Caracterización (E1)
* **Fecha:** 20/10/2026
* **Herramienta:** Claude Sonnet 3.5
* **Prompt enviado:**
  > "Analiza el archivo `src/pedidos/antes/servicio.py`. Ejecuta un diagnóstico de olores de código (Code Smells) de Fowler y calcula la complejidad ciclomática del método `procesar_pedido_multipuesto`. Genera un conjunto de pruebas de caracterización que congelen el comportamiento actual antes de refactorizar."
* **Propuesta de la IA:** 
  - Detectó *Long Method* y *Complex Conditional* en `procesar_pedido_multipuesto` (CC=14, clasificación C de radon).
  - Detectó *Divergent Change*: el servicio cambia si cambia la lógica de pedidos, si cambia la pasarela Yape o si cambia la mensajería.
  - Generó 8 pruebas de caracterización en `tests/test_comportamiento.py`.
* **Evaluación del Equipo:**
  - El análisis fue exacto y riguroso.
  - Las pruebas de caracterización revelaron que si el medio de pago era inválido, el pedido quedaba parcialmente confirmado en memoria antes de fallar.
* **Decisión:** Aceptada. Las pruebas se establecieron como red de seguridad fija.

---

### Interacción 2 — Desacoplamiento de Pagos: Strategy, Adapter y Factory (E2)
* **Fecha:** 21/10/2026
* **Herramienta:** Gemini 1.5 Pro
* **Prompt enviado:**
  > "Refactoriza el manejo de pagos en `src/pedidos/pagos.py` aplicando el patrón Strategy para los algoritmos de cobro, Adapter para unificar las APIs incompatibles de Yape y Plin, y Factory para instanciar el adaptador según el string de entrada. La solución debe cumplir Open/Closed (OCP)."
* **Propuesta de la IA:** 
  - Declaró el protocolo `PasarelaPago` con método `cobrar(monto, referencia)`.
  - Creó los adaptadores `YapeAdapter` y `PlinAdapter` envolviendo los clientes crudos de `externos.py`.
  - Diseñó `FabricaPasarelas` con un registro tipo diccionario dinámico.
* **Evaluación del Equipo:**
  - Se detectó que la IA no incluyó reintentos en caso de `TimeoutError` en las pasarelas móviles. El equipo solicitó añadir un bucle de reintento de 3 intentos.
  - Se confirmó que agregar un nuevo medio de pago (como Plin v2 o QR) solo requiere una nueva clase y registrarla en la fábrica, sin tocar el código central.
* **Decisión:** Aceptada con la adición de reintentos ante timeout.

---

### Interacción 3 — Máquina de Estados de Pedidos con Patrón State (E3)
* **Fecha:** 22/10/2026
* **Herramienta:** Claude Sonnet 3.5
* **Prompt enviado:**
  > "Reemplaza los condicionales de cambio de estado en `src/pedidos/estados.py` por el patrón State de GoF. El pedido atraviesa: Borrador -> Confirmado -> Pagado -> EnPreparacion -> Entregado (o Cancelado). Cada estado debe ser una clase con sus transiciones permitidas."
* **Propuesta de la IA:** Implementó la clase abstracta `EstadoPedido` y sus estados concretos (`EstadoBorrador`, `EstadoConfirmado`, `EstadoPagado`, `EstadoCancelado`). Cada estado define métodos como `confirmar()`, `pagar()`, `cancelar()`.
* **Evaluación del Equipo:**
  - La implementación elimina de raíz las estructuras `if estado == 'BORRADOR': ... elif estado == 'PAGADO': ...`.
  - Se verificó que intentar pagar un pedido ya cancelado lance la excepción tipada `TransicionInvalidaError`.
* **Decisión:** Aceptada íntegramente.

---

### Interacción 4 — Notificaciones Desacopladas con Patrón Observer (E4)
* **Fecha:** 23/10/2026
* **Herramienta:** Gemini 1.5 Pro
* **Prompt enviado:**
  > "Implementa en `src/pedidos/eventos.py` el patrón Observer para desacoplar la confirmación del pedido del envío de notificaciones por WhatsApp y alertas a repartidores. Si un suscriptor falla, no debe interrumpir a los demás."
* **Propuesta de la IA:** Creó `PublicadorEventos`, la interfaz `SuscriptorEvento` y dos observadores concretos: `NotificadorWhatsApp` y `NotificadorRepartidor`.
* **Evaluación del Equipo:**
  - La IA inicialmente propagaba cualquier excepción del suscriptor, lo cual abortaba la confirmación de la venta si WhatsApp fallaba.
  - El equipo corrigió el publicador para capturar errores de suscriptores individuales y registrarlos en log sin romper el hilo principal.
* **Decisión:** Aceptada con la corrección del aislamiento de excepciones.

---

### Interacción 5 — Capa de IA, Caché Decorator y Guardrails (E5)
* **Fecha:** 24/10/2026
* **Herramienta:** Claude Sonnet 3.5
* **Prompt enviado:**
  > "Diseña en `src/pedidos/ia.py` un componente de recomendación de productos asistido por IA. Aplica Strategy para proveedores LLM intercambiables, Decorator para caché de respuestas idénticas y Chain of Responsibility para guardrails que validen entradas (prompt injection, vacíos) y salidas (alucinaciones de precios S/ 0.00 y formato)."
* **Propuesta de la IA:**
  - `ProveedorLLM` (Protocolo) con implementaciones `LLMSimulado`, `AdaptadorOpenAI`, `AdaptadorGemini`.
  - `LLMConCache` (Decorator) que normaliza consultas y ahorra llamadas externas.
  - Cadena de 5 guardrails de entrada y 3 de salida (`GuardrailLongitud`, `GuardrailInyeccion`, `GuardrailPreciosValidos`).
* **Evaluación del Equipo:**
  - El diseño previene ataques de prompt injection y alucinaciones críticas donde el modelo invente productos gratis (S/ 0.00).
  - Se crearon 38 pruebas unitarias exhaustivas en `tests/test_ia.py` que validan cada eslabón de la cadena.
* **Decisión:** Aceptada con excelentes resultados en la suite de pruebas.

---

### Interacción 6 — Métricas Radon y Combate a la "Patternitis" (E6)
* **Fecha:** 25/10/2026
* **Herramienta:** Gemini 1.5 Pro
* **Prompt enviado:**
  > "Calcula con `radon` la complejidad ciclomática del código antes y después de aplicar patrones. Sugiere qué otros patrones GoF podríamos agregar al sistema."
* **Propuesta de la IA:** La IA entregó las métricas (reducción de 14 a 2 en CC) y propuso agregar:
  1. *Singleton* para la fábrica de pasarelas.
  2. *Abstract Factory* para familias de procesadores de pago.
* **Evaluación del Equipo:**
  - **Identificación de Patternitis:** El equipo analizó críticamente ambas sugerencias. `Singleton` genera estado global mutable perjudicial para las pruebas concurrentes con `pytest`. `Abstract Factory` introduce capas innecesarias dado que solo se maneja una familia de pasarelas.
* **Decisión:** Rechazo fundamentado de ambos patrones y registro de las métricas en `docs/design/patrones/metricas.md`.
