# INFORME TÉCNICO: REFACTORIZACIÓN CON PATRONES DE DISEÑO GOF Y CAPA DE IA RESILIENTE

**Asignatura:** Construcción de Software (2026B)  
**Institución:** Universidad Nacional de San Agustín de Arequipa  
**Facultad:** Facultad de Ingeniería de Producción y Servicios  
**Escuela:** Escuela Profesional de Ingeniería de Sistemas  
**Docente:** Mg. Antonio Arroyo Paz  
**Grupo:** 07  
**Caso de Estudio:** San Camilo en Línea  
**Etiqueta de Versión:** `v0.7-patrones`  
**Fecha:** Octubre 2026  

---

## 1. Resumen Ejecutivo y Objetivos

El presente informe documenta la refactorización arquitectónica y de diseño orientada a objetos aplicada al módulo de procesamiento de pedidos y pagos de la plataforma **San Camilo en Línea**. A partir de una versión monolítica procedural inicial afectada por acoplamiento severo y alta complejidad ciclomática ($CC=14$, clasificación C), se aplicaron patrones de diseño del Gang of Four (GoF) y de ingeniería de inteligencia artificial:

1. **Strategy, Adapter y Factory:** Desacoplamiento de las pasarelas de pago digitales (Yape y Plin) garantizando cumplimiento estricto del Principio Abierto/Cerrado (OCP).
2. **State:** Modelado formal de las transiciones del ciclo de vida del pedido multi-puesto eliminando condicionales anidados.
3. **Observer:** Desacoplamiento asíncrono de eventos de notificación comercial y logística.
4. **Decorator y Chain of Responsibility (Capa de IA):** Aislamiento de proveedores LLM, caché de respuestas frecuentes y cadena de guardrails de entrada/salida para mitigar inyecciones de prompts y alucinaciones de precios.

La refactorización redujo la complejidad ciclomática del método principal en un **$85.7\%$** ($CC$ de 14 a 2, clasificación A) y cuenta con una red de seguridad automatizada de **58 pruebas unitarias** ejecutadas satisfactoriamente en `pytest`.

---

## 2. Diagnóstico de Olores de Código (Versión "Antes")

En la versión inicial (`src/pedidos/antes/servicio.py`), el método `procesar_pedido_multipuesto` acumulaba múltiples violaciones a los principios SOLID y olores de código identificados por Fowler (2018):

* **Método Largo y Condicionales Complejos (*Long Method / Complex Conditionals*):** 88 líneas en un único método con bifurcaciones `if/elif/else` anidadas para determinar si el cliente pagaba con Yape, Plin o contraentrega, calcular comisiones y cambiar estados. Complejidad ciclomática medida con `radon`: **14 (C)**.
* **Cambio Divergente (*Divergent Change*):** La clase cambiaba por tres motivos distintos: cambios en la regla de negocio de pedidos, cambios en las credenciales o formato de la API de Yape, o cambios en la plantilla de mensajes de WhatsApp.
* **Acoplamiento Fuerte a Implementaciones Concretas:** Invocación directa a funciones de bajo nivel sin interfaces intermedias, impidiendo la simulación con dobles de prueba (*mocks*) en pruebas unitarias.

---

## 3. Patrones de Diseño Aplicados y Arquitectura de la Solución

### 3.1. Strategy + Adapter + Factory (`src/pedidos/pagos.py`)
* **Strategy:** Se definió la abstracción `PasarelaPago` (Protocol) con el contrato `cobrar(monto, referencia) -> ComprobantePago`.
* **Adapter:** Las clases `YapeAdapter` y `PlinAdapter` adaptan las interfaces propietarias de cada billetera digital al contrato unificado, incorporando además tolerancia a fallos con hasta 3 reintentos ante `TimeoutError`.
* **Factory:** La clase `FabricaPasarelas` centraliza la resolución e instanciación del adaptador correspondiente según el método solicitado por el cliente.
* **Impacto OCP:** Para incorporar un nuevo método de pago (por ejemplo, pago con tarjeta o QR interoperable), se crea una nueva clase que implemente `PasarelaPago` y se registra en la fábrica, requiriendo **0 modificaciones** en el núcleo de pedidos.

### 3.2. State Pattern (`src/pedidos/estados.py`)
* Se sustituyó la variable de estado primitiva y las sentencias condicionales por la jerarquía polimórfica `EstadoPedido`:
  - `EstadoBorrador`: Permite confirmación y cancelación.
  - `EstadoConfirmado`: Permite pago y cancelación con liberación de stock.
  - `EstadoPagado`: Permite inicio de preparación y despacho.
  - `EstadoCancelado`: Estado terminal; cualquier operación posterior lanza `TransicionInvalidaError`.

### 3.3. Observer Pattern (`src/pedidos/eventos.py`)
* El `PublicadorEventos` emite eventos de dominio (`PedidoConfirmado`, `PedidoPagado`) a una lista de suscriptores registrados (`NotificadorWhatsApp`, `NotificadorLogisticaReparto`).
* Se garantiza que la falla o caída de un suscriptor externo (como la API de WhatsApp) sea capturada y registrada en bitácora sin bloquear la confirmación de la venta para el cliente.

### 3.4. Capa de IA con Decorator y Chain of Responsibility (`src/pedidos/ia.py`)
* **Strategy:** `ProveedorLLM` permite alternar dinámicamente entre `LLMSimulado`, `AdaptadorGemini` y `AdaptadorOpenAI`.
* **Decorator de Caché (`LLMConCache`):** Intercepta consultas normalizadas idénticas, retornando respuestas cacheadas en memoria para reducir latencia y costo de tokens.
* **Chain of Responsibility (Guardrails):**
  - **Entrada:** `GuardrailEntradaNoVacia`, `GuardrailLongitudMaxima` (límite de 500 caracteres) y `GuardrailAntiInyeccion` (bloqueo de inyecciones de prompt y sentencias SQL/XSS).
  - **Salida:** `GuardrailFormatoRespuesta` y `GuardrailPreciosValidos` (bloqueo estricto de alucinaciones donde el LLM invente productos a precio cero: S/ 0.00).

---

## 4. Métricas Cuantitativas de Refactorización (`radon cc`)

```
========================================================================================
COMPARATIVA ANTES VS DESPUÉS (RADON CC & SLOC)
========================================================================================
Métrica                              Antes (Monolito)    Después (Patrones)     Variación
----------------------------------------------------------------------------------------
Complejidad Método Principal              14 (C)                2 (A)           -85.7 %
Complejidad Ciclomática Promedio          8.5 (B)               1.8 (A)         -78.8 %
Líneas de Código Lógicas (SLOC)          88 líneas             142 líneas       +61.3 %
Archivos Fuente                          1 archivo             4 módulos        +3 archivos
Pruebas Unitarias Automatizadas           8 tests               58 tests        +625 %
Porcentaje de Cobertura / Éxito          100 %                 100 % (58/58)     Verde
========================================================================================
```

---

## 5. Análisis Honesto de Trade-offs y Anti-Patternitis

* **Beneficios Obtenidos:** Alta modificabilidad, aislamiento de fallos, extensibilidad sin riesgo de regresión y cumplimiento de estándares de arquitectura limpia.
* **Sobrecostos Aceptados:** Incremento del $61.3\%$ en líneas lógicas de código (SLOC) y mayor cantidad de clases para navegar en el IDE.
* **Patrones Rechazados:**
  - *Singleton:* Rechazado en la fábrica para no introducir estado global mutable que contamine las pruebas en `pytest`.
  - *Abstract Factory:* Rechazado debido a que no existen múltiples familias de pasarelas interdependientes; adoptarlo habría constituido un caso típico de *patternitis*.

---

## 6. Conclusiones

1. La refactorización transformó un código frágil en una arquitectura modular, extensible y altamente mantenible, cumpliendo el principio Open/Closed.
2. La integración de la Capa de IA con guardrails formaliza el principio de *defensa en profundidad*, tratando las respuestas generativas como entradas no confiables del sistema.
3. El conjunto de 58 pruebas automatizadas certifica que la funcionalidad del negocio se preservó al 100% durante el proceso.

---

## 7. Referencias

* Fowler, M. (2018). *Refactoring: Improving the design of existing code* (2nd ed.). Addison-Wesley.
* Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design patterns: Elements of reusable object-oriented software*. Addison-Wesley.
* Martin, R. C. (2017). *Clean architecture: A craftsman's guide to software structure and design*. Prentice Hall.
* McCabe, T. J. (1976). *A complexity measure*. IEEE Transactions on Software Engineering, SE-2(4), 308–320.
