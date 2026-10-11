# E7 - Bitacora de Interacciones con IA

Registro de las interacciones con herramientas de inteligencia artificial utilizadas durante el desarrollo de los entregables. Se documenta el prompt, la respuesta resumida y la evaluacion del resultado.

---

## Interaccion 1 - Generacion del diagrama de clases (E1)

**Fecha:** 2026-10-10
**Herramienta:** Antigravity (Gemini / Claude)
**Prompt enviado:**

> "Dado el caso 'San Camilo en Linea' (pedidos multi-puesto, pago unico con Yape, notificaciones WhatsApp), genera un diagrama de clases PlantUML con minimo 6 clases, 1 interfaz y 1 enumeracion que cubra el modulo de pedidos."

**Respuesta resumida:** La IA propuso las clases `Cliente`, `Puesto`, `Producto`, `PedidoGlobal`, `PedidoPuesto`, `ItemPedido`, `Pago`, la interfaz `PasarelaPago <<puerto>>` y la enumeracion `EstadoPedidoPuesto`. Incluyo relaciones de composicion y asociacion con multiplicidades.

**Evaluacion:**
- Cumplio el minimo de clases, interfaz y enumeracion.
- Las relaciones de composicion `PedidoGlobal *-- PedidoPuesto` son semanticamente correctas.
- Inicialmente omitio `ServicioPedidos`; se solicito anadirlo en una segunda iteracion.
- **Decision:** Se acepto la propuesta con la adicion del servicio y dos interfaces adicionales (`RepositorioPedidos`, `NotificadorWhatsApp`).

---

## Interaccion 2 - Generacion del esqueleto Python (E6)

**Fecha:** 2026-10-10
**Herramienta:** Antigravity (Claude Sonnet)
**Prompt enviado:**

> "A partir del archivo `clases.puml` y la maquina de estados `estados-PedidoPuesto.mmd`, genera el esqueleto del modulo `pedidos` en Python usando `dataclasses`, `enum` y `Protocol`. Incluye validacion de transiciones de estado y reserva de stock."

**Respuesta resumida:** La IA genero el archivo `src/pedidos/models.py` con todas las entidades, la enumeracion con sus literales, el diccionario de transiciones validas dentro de `PedidoPuesto.cambiar_estado()`, el metodo `reservar_stock` con validacion, y el `ServicioPedidos` con inyeccion de dependencias a traves de puertos `Protocol`.

**Evaluacion:**
- Codigo Python idiomatico y correctamente tipado.
- Los puertos estan modelados como `Protocol`, respetando la inversion de dependencias.
- La IA inicialmente no incluyo el metodo `liberar_stock` en el flujo de cancelacion de `PedidoGlobal.cancelar()`; se corrigio en revision.
- **Decision:** Se acepto con la correccion del flujo de cancelacion.

---

## Interaccion 3 - Diagrama de paquetes y verificacion de ciclos (E5)

**Fecha:** 2026-10-10
**Herramienta:** Antigravity (Claude Sonnet)
**Prompt enviado:**

> "Genera un diagrama de paquetes PlantUML para el monolito modular de ADR-001 con los modulos: Catalogo, Pedidos, Pagos, Notificaciones y Entregas. Incluye la capa API, la capa de Infraestructura con adaptadores, y verifica que no existan dependencias ciclicas."

**Respuesta resumida:** La IA propuso la estructura en tres capas (`api`, modulos de aplicacion, `infraestructura`) con flechas de dependencia unidireccionales. Explico que la capa de infraestructura implementa los puertos declarados en los modulos, evitando que los modulos conozcan las implementaciones concretas.

**Evaluacion:**
- No hay ciclos: `infraestructura -> modulos -> api` (nunca al reves).
- Se alineo con el principio de inversion de dependencias del ADR-001.
- La IA sugirio conectar `notificaciones -> pedidos` para "escuchar eventos", lo que crearia un ciclo con `pedidos -> notificaciones`. Se rechazo y se mantuvo solo `pedidos -> notificaciones`.
- **Decision:** Se rechazo la sugerencia de dependencia inversa; se mantuvo la unidireccionalidad.

---

## Interaccion 4 - Auditoria de consistencia C1-C5 (E7)

**Fecha:** 2026-10-10
**Herramienta:** Antigravity (Claude Sonnet)
**Prompt enviado:**

> "Audita los cinco diagramas (clases, secuencia, estados, actividades, paquetes) contra las reglas C1 (nomenclatura), C2 (estados), C3 (modulos ADR), C4 (sin ciclos) y C5 (trazabilidad historia). Indica hallazgos y si pasan o fallan."

**Respuesta resumida:** La IA reviso cada regla sistematicamente. Para C4 construyo el grafo de dependencias y verifico la ausencia de ciclos. Para C5 raztreo cada criterio de aceptacion a clases especificas en el diagrama de clases y la maquina de estados.

**Evaluacion:**
- La auditoria fue exhaustiva y detecto la propuesta de ciclo en C4 (interaccion 3) como un hallazgo potencial.
- Todas las reglas pasaron con la arquitectura final.
- La IA senalo que C5 requeria que el equipo definiera explicitamente la correspondencia criterio-diagrama; no pudo inferirla automaticamente sin el texto de la historia.
- **Decision:** Se documento la trazabilidad manualmente en `consistencia.md`.

---

## Interaccion 5 - Analisis de diferencias del round-trip (E6)

**Fecha:** 2026-10-10
**Herramienta:** Antigravity (Claude Sonnet)
**Prompt enviado:**

> "Compara el diagrama de diseno `clases.puml` con el diagrama generado por pyreverse `classes_pedidos.puml`. Lista al menos 3 diferencias concretas y explica si son esperadas o indican un problema de fidelidad."

**Respuesta resumida:** La IA identifico cinco diferencias: (D1) perdida de estereotipos UML, (D2) enumeracion sin literales, (D3) multiplicidades ausentes, (D4) dependencias de uso del servicio no capturadas, (D5) adaptadores concretos ausentes (correctamente, pues pertenecen a otro paquete).

**Evaluacion:**
- Las diferencias identificadas son precisas y bien explicadas.
- La IA reconocio que D5 no es un problema sino evidencia de que la separacion de capas funciona.
- Sirvio como base directa para la seccion 3 del `round-trip.md`.
- **Decision:** Se adopto integramente el analisis con revision editorial minima.

---

## Resumen de interacciones

| N | Entregable | Tipo de uso | Resultado | Accion tomada |
|---|---|---|---|---|
| I1 | E1 - Diagrama de clases | Generacion inicial | Aceptado con correccion | Anadir `ServicioPedidos` e interfaces adicionales |
| I2 | E6 - Esqueleto Python | Generacion de codigo | Aceptado con correccion | Corregir flujo de cancelacion |
| I3 | E5 - Diagrama de paquetes | Validacion arquitectonica | Aceptado; sugerencia rechazada | Rechazar dependencia ciclica propuesta |
| I4 | E7 - Auditoria C1-C5 | Analisis de consistencia | Aceptado | Documentar trazabilidad manualmente |
| I5 | E6 - Analisis round-trip | Analisis comparativo | Aceptado integro | Incorporar al `round-trip.md` |

> **Reflexion:** La IA acelero la generacion de artefactos, pero requirio revision critica en cada paso. Las propuestas rechazadas (ciclo de dependencia, omision de metodos) confirman que la IA no puede reemplazar el juicio de diseno del arquitecto, solo apoyarlo.
