# ADR-005: Patrones de diseño para la capa de IA (Strategy, Decorator, Chain of Responsibility)

- Estado: Aceptado
- Fecha: 2026-10-25
- Decisores: Kennedy Chirinos Rojas
- Laboratorio: 07 — Patrones de Diseño

## Contexto

El sistema San Camilo en Línea incorpora un componente de inteligencia artificial para asistir a los clientes durante la consulta de productos y la creación de pedidos. Este componente debe interactuar con modelos de lenguaje (LLM) externos para generar sugerencias y respuestas contextuales.

Se identifican tres requisitos arquitectónicos clave para la capa de IA:

1. **Intercambiabilidad de proveedores:** El equipo necesita poder cambiar de proveedor de LLM (OpenAI, Gemini, modelos locales) sin modificar la lógica del servicio, y disponer de un simulado para pruebas unitarias sin dependencias externas ni costos de API.

2. **Optimización de costos:** Las consultas repetidas (ej. "¿qué frutas hay?") no deben invocar al LLM cada vez. Se requiere un mecanismo de caché que sea transparente para el servicio consumidor.

3. **Seguridad y calidad de respuestas:** Las entradas del usuario y las salidas del LLM deben pasar por filtros de validación que detecten inyecciones de prompts, contenido prohibido, alucinaciones, precios inválidos y respuestas malformadas. Estos filtros deben ser extensibles sin modificar los existentes.

El componente se integra dentro del monolito modular (ADR-001) como parte del módulo `pedidos`, respetando la inversión de dependencias establecida.

## Alternativas consideradas

### Para la intercambiabilidad de proveedores LLM

1. **Strategy / Adapter:** Definir una interfaz abstracta `ProveedorLLM` con el método `generar_respuesta()`. Cada proveedor concreto (OpenAI, Gemini, simulado) implementa la interfaz. El servicio de IA depende solo de la abstracción.
2. **Clase monolítica con condicionales:** Un único proveedor con bloques `if/elif` para cada API. Rápido de implementar, pero viola el Principio Abierto/Cerrado y dificulta las pruebas.
3. **Factory Method puro:** Una fábrica que instancia el proveedor correcto. Resuelve la creación pero no el desacoplamiento en tiempo de ejecución.

**Decisión:** Strategy / Adapter. Permite inyectar cualquier proveedor en tiempo de ejecución y facilita las pruebas con `LLMSimulado` sin condicionales ni dependencias de red.

### Para la optimización de consultas repetidas

1. **Decorator (Caché):** Envolver el proveedor LLM con un decorador `LLMConCache` que almacena resultados y los devuelve ante entradas idénticas. Es transparente: el servicio consumidor no distingue entre un proveedor con o sin caché.
2. **Caché en el servicio de aplicación:** Almacenar respuestas directamente en `ServicioIA`. Funciona, pero mezcla la responsabilidad de caché con la lógica de orquestación.
3. **Caché externo (Redis/Memcached):** Eficiente en producción pero excesivo para el MVP y agrega una dependencia de infraestructura.

**Decisión:** Decorator (Caché). Respeta el Principio de Responsabilidad Única, es composable con cualquier proveedor y no requiere infraestructura adicional.

### Para la validación de entradas y salidas

1. **Chain of Responsibility (Guardrails):** Cadena de manejadores donde cada guardrail valida un aspecto (entrada vacía, longitud, contenido prohibido, formato de respuesta, precios válidos). Si un eslabón detecta un problema, detiene la cadena y reporta el error. Nuevos guardrails se agregan sin modificar los existentes.
2. **Validación centralizada con condicionales:** Un único método con `if/elif` para cada regla. Simple pero no extensible y viola el Principio Abierto/Cerrado.
3. **Middleware / Pipeline genérico:** Similar en concepto pero con mayor complejidad de abstracción que la necesaria para el MVP.

**Decisión:** Chain of Responsibility. Permite agregar, remover o reordenar guardrails sin cambiar el código existente. Cada guardrail tiene una única responsabilidad y es testeable de forma independiente.

## Decision

Se implementan tres patrones de diseño complementarios en el archivo `src/pedidos/ia.py`:

| Patrón | Rol | Clases principales |
|---|---|---|
| **Strategy / Adapter** | Intercambiar proveedores LLM | `ProveedorLLM` (ABC), `LLMSimulado`, `AdaptadorOpenAI`, `AdaptadorGemini` |
| **Decorator (Caché)** | Evitar consultas repetidas | `LLMConCache` (hereda `ProveedorLLM`, decora otro `ProveedorLLM`) |
| **Chain of Responsibility** | Validar entradas y salidas | `Guardrail` (ABC), `GuardrailEntradaVacia`, `GuardrailLongitudMaxima`, `GuardrailContenidoProhibido`, `GuardrailFormatoRespuesta`, `GuardrailPreciosValidos` |

El `ServicioIA` orquesta los tres patrones:
1. Valida la entrada con la cadena de guardrails de entrada.
2. Consulta al proveedor LLM (decorado con caché).
3. Valida la salida con la cadena de guardrails de salida.
4. Retorna `RespuestaIA` con metadata de validación para trazabilidad.

### Criterios de cumplimiento

- Las pruebas unitarias deben pasar al 100 % con el `LLMSimulado`, sin dependencias de red ni credenciales.
- El caché debe demostrar que ante una misma consulta, el LLM subyacente se invoca exactamente una vez.
- Los guardrails deben bloquear entradas vacías, inyecciones SQL/XSS, respuestas con alucinaciones, precios inválidos (≤ 0) y contenido que filtre credenciales.
- Agregar un nuevo guardrail no debe requerir modificar ningún guardrail existente.

## Consecuencias

- **Positivas:** Desacoplamiento total del proveedor de LLM; el equipo puede ejecutar el 100 % de las pruebas sin credenciales ni costos de API.
- **Positivas:** El Decorator de caché reduce invocaciones al LLM y es composable: `LLMConCache(LLMSimulado())` o `LLMConCache(AdaptadorOpenAI(...))`.
- **Positivas:** Los guardrails son extensibles (Open/Closed Principle) y cada uno es testeable de forma independiente.
- **Positivas:** La metadata de validación en `RespuestaIA` permite auditoría y trazabilidad de decisiones del componente de IA.
- **Negativas / riesgos:** El caché en memoria no persiste entre reinicios del servidor; en producción podría necesitarse un caché distribuido.
- **Negativas / riesgos:** La cadena de guardrails agrega complejidad; si se acumulan demasiados eslabones, la latencia podría incrementarse.
- **Mitigación:** Monitorear el tamaño del caché y la cantidad de guardrails. Si es necesario, reemplazar el caché en memoria por uno distribuido sin cambiar la interfaz.

## Plan de revisión

La decisión se revisará si:
- Se integra un proveedor LLM real y el caché en memoria resulta insuficiente.
- Se requieren guardrails con estado (ej. rate limiting por usuario), lo que podría motivar un patrón adicional.
- El número de guardrails supera 10, en cuyo caso se evaluará agruparlos en pipelines nombrados.

