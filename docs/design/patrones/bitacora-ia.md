# Bitácora de Interacciones con IA — Laboratorio 07 (Patrones de Diseño)

Registro de las interacciones con herramientas de inteligencia artificial utilizadas durante el desarrollo del bloque "Capa de IA, Guardrails y Cierre Arquitectónico" (Entregables E5, E7 de IA y E8).

**Responsable:** Kennedy Chirinos Rojas
**Herramienta:** Antigravity (Claude Opus 4.6)
**Fecha:** 2026-10-25

---

## Interacción 1 — Exploración del repositorio y plan de acción

**Prompt enviado:**

> "Actúa como un Arquitecto de Software Senior. Revisa y analiza la estructura completa de mi directorio actual para entender de qué trata el sistema y cómo está organizado. Identifica el dominio del negocio, las entidades existentes y cómo se conectan los componentes."

**Respuesta resumida:** La IA exploró recursivamente el repositorio, leyó `README.md`, `models.py`, `clases.puml`, `paquetes.puml`, los ADR existentes y la bitácora previa. Identificó correctamente el dominio (Mercado San Camilo), las 12 clases/tipos del módulo `pedidos`, la arquitectura monolito modular (ADR-001) y que no existían las carpetas `tests/` ni `docs/design/patrones/`.

**Evaluación:**
- El análisis fue exhaustivo y preciso.
- Identificó correctamente que faltaban `pyproject.toml`, `__init__.py` y la configuración de pytest.
- Propuso un plan de acción con 10 pasos ordenados y rutas exactas de archivos.
- **Decisión:** Se aceptó el plan íntegramente.

---

## Interacción 2 — Diseño e implementación de `ia.py` (E5)

**Prompt enviado:**

> "Diseña e implementa en `ia.py` la arquitectura para el componente de IA aplicando tres patrones: Strategy/Adapter para desacoplar proveedores LLM, Decorator de Caché para interceptar consultas repetidas, y Chain of Responsibility para guardrails de validación de entradas y salidas."

**Respuesta resumida:** La IA generó `src/pedidos/ia.py` con:
- Interfaz abstracta `ProveedorLLM` y tres implementaciones (LLMSimulado, AdaptadorOpenAI, AdaptadorGemini).
- Decorator `LLMConCache` que envuelve cualquier `ProveedorLLM` con normalización de clave y capacidad configurable.
- Clase abstracta `Guardrail` con encadenamiento fluido y 5 implementaciones concretas: EntradaVacía, LongitudMáxima, ContenidoProhibido, FormatoRespuesta, PreciosVálidos.
- `ServicioIA` como orquestador que integra los 3 patrones.
- Funciones de fábrica para configuración predeterminada.

**Evaluación:**
- El código es idiomático, tipado y bien documentado con docstrings.
- Los guardrails de salida incluyen validadores específicos del dominio (precios S/ 0.00, marcadores de alucinación).
- La IA incluyó correctamente el `GuardrailPreciosValidos` con regex para el formato de precios peruano (S/).
- Los adaptadores concretos (OpenAI, Gemini) lanzan `NotImplementedError` para evitar dependencias externas en las pruebas.
- **Decisión:** Se aceptó sin correcciones.

---

## Interacción 3 — LLM simulado y pruebas unitarias (E5)

**Prompt enviado:**

> "Implementa un LLM simulado que permita simular respuestas válidas, alucinaciones, precios inválidos y violaciones de seguridad. Crea las pruebas unitarias con pytest que validen los guardrails y el caché."

**Respuesta resumida:** La IA generó:
- `tests/conftest.py` con fixtures para LLMSimulado (9 respuestas predefinidas), LLMConCache y ServicioIA completo.
- `tests/test_ia.py` con 38 pruebas organizadas en 5 clases:
  - `TestStrategy` (7 tests): intercambiabilidad de proveedores, conteo de invocaciones.
  - `TestDecoratorCache` (6 tests): caché no re-invoca LLM, normalización, capacidad máxima, limpieza.
  - `TestGuardrailsEntrada` (6 tests): entrada vacía, longitud excesiva, inyección SQL/XSS.
  - `TestGuardrailsSalida` (7 tests): alucinación, precio cero, precio negativo, credenciales filtradas, respuesta corta.
  - `TestIntegracionServicioIA` (5 tests): flujo completo, caché integrado, metadata de validación.
  - `TestGuardrailsIndividuales` (7 tests): tests unitarios aislados de cada guardrail.

**Evaluación:**
- Los 38 tests pasaron en 0.07 segundos.
- La cobertura cubre los tres patrones y sus interacciones.
- El test `test_cache_no_reinvoca_llm_en_consulta_repetida` verifica explícitamente que `llm_simulado.invocaciones == 1` tras dos consultas idénticas.
- El test `test_guardrail_entrada_bloquea_antes_de_invocar_llm` verifica que si la entrada falla, el LLM no se invoca (invocaciones == 0).
- **Decisión:** Se aceptó sin correcciones.

---

## Interacción 4 — Diagramas PlantUML y pyreverse (E7)

**Prompt enviado:**

> "Elabora el diagrama de clases PlantUML para la arquitectura del componente de IA e indícame los comandos para usar pyreverse sobre el código."

**Respuesta resumida:** La IA generó `docs/design/patrones/ia-patrones.puml` con diagrama completo incluyendo paquetes por patrón, estereotipos UML, relaciones de herencia y composición, y notas explicativas. Para pyreverse, ejecutó el comando:

```
python -c "from pylint.pyreverse.main import Run; Run(['-o', 'puml', '-p', 'pedidos_ia', 'pedidos.ia'])"
```

que generó `classes_pedidos_ia.puml` con las clases detectadas automáticamente.

**Evaluación:**
- El diagrama manual (`ia-patrones.puml`) es más rico que el generado por pyreverse: incluye estereotipos, paquetes y notas.
- Pyreverse detectó correctamente las 12 clases y las relaciones de herencia pero no capturó composiciones ni multiplicidades (limitación conocida, documentada en el round-trip del Lab 05).
- La IA tuvo dificultades técnicas con el PATH de pyreverse en Windows pero las resolvió usando invocación vía subprocess.
- **Decisión:** Se aceptó. Se conservan ambos diagramas (manual y generado) para comparación round-trip.

---

## Interacción 5 — ADR-005 y documentación de cierre (E8)

**Prompt enviado:**

> "Redacta el ADR-005 justificando las decisiones arquitectónicas de la capa de IA. Actualiza el README.md con la sección del Laboratorio 07."

**Respuesta resumida:** La IA redactó:
- ADR-005 con el formato establecido (Contexto, Alternativas, Decisión, Consecuencias, Plan de revisión).
- Para cada patrón documentó 3 alternativas con justificación de la selección.
- Criterios de cumplimiento verificables vinculados a las pruebas.
- Actualización del README con tabla de entregables y estado.

**Evaluación:**
- El ADR sigue el formato consistente con ADR-001, 002 y 003.
- Las alternativas descartadas son realistas y la justificación es técnicamente sólida.
- Las consecuencias negativas identifican riesgos reales (caché en memoria, acumulación de guardrails).
- **Decisión:** Se aceptó con revisión editorial mínima.

---

## Resumen de interacciones

| N | Entregable | Tipo de uso | Resultado | Acción tomada |
|---|---|---|---|---|
| I1 | Plan de acción | Exploración y planificación | Aceptado íntegro | Seguir el plan propuesto |
| I2 | E5 - `ia.py` | Generación de código | Aceptado sin correcciones | Integrar directamente |
| I3 | E5 - Tests | Generación de pruebas | Aceptado sin correcciones | 38/38 tests en verde |
| I4 | E7 - Diagramas | Generación PlantUML + pyreverse | Aceptado | Conservar ambos diagramas |
| I5 | E8 - ADR-005 y README | Documentación arquitectónica | Aceptado con revisión mínima | Integrar con ajustes editoriales |

> **Reflexión:** La IA fue especialmente efectiva en este laboratorio porque el contexto estaba bien definido por los laboratorios anteriores (dominio, ADRs, historia de usuario). La mayor dificultad fue técnica (compatibilidad de pyreverse con Windows), no conceptual. Los patrones propuestos se alinean correctamente con los principios SOLID y con la arquitectura monolito modular del ADR-001. Todas las propuestas fueron verificadas con pruebas automatizadas antes de aceptarlas.

