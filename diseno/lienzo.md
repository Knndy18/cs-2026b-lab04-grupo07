# Lienzo de Diseño del Sistema Agéntico: San Camilo en Línea

Este lienzo documenta las 7 decisiones arquitectónicas y de diseño del sistema agéntico para la plataforma **San Camilo en Línea** (Mercado San Camilo), siguiendo las directrices de Albada (2025), Koenigstein (2026) y Grootendorst & Alammar (2026).

---

## 1. Lienzo de Decisiones de Diseño

| Decisión de diseño | Elección para San Camilo en Línea | Justificación técnica |
|---|---|---|
| **1. ¿Agente o flujo de trabajo?** | **Agente** para resolución y depuración autónoma de incidencias; **Flujo de trabajo fijo** para operaciones transaccionales rutinarias. | La resolución de incidencias en el repositorio requiere exploración diagnóstica: inspeccionar código, formular hipótesis, reproducir fallos y verificar contratos. Los pasos no se conocen de antemano (Anthropic, 2024). Por el contrario, tareas transaccionales como cobrar por Yape o notificar pedidos por WhatsApp siguen flujos fijos rígidos y deterministas donde un agente añadiría costo y latencia innecesarios. |
| **2. Arquetipo** | **Planificador-Ejecutor + ReAct** (Sección 1.3 de la guía). | Un planificador inicial descompone el issue en un conjunto claro y acotado de subobjetivos legibles y económicos. El ejecutor implementa el bucle ReAct (Razonamiento $\to$ Acción $\to$ Observación), lo que le permite reaccionar flexiblemente ante fallos de pruebas, errores de sintaxis o salidas inesperadas antes de comprometer cambios. |
| **3. Herramientas** | Conjunto mínimo con principio de menor privilegio: `listar_archivos`, `leer_archivo`, `buscar`, `editar_archivo`, `ejecutar_pruebas`, `ver_cambios`, `ejecutar_comando`. | Mantener pocas herramientas con alcance mínimo maximiza la precisión en la selección de llamadas (tool calling) y reduce alucinaciones (Albada, 2025). Todas las operaciones de archivos están confinadas a un sandbox estricto. La ejecución de comandos se limita a una lista blanca (`pytest`, `radon`, `lint-imports`, `git diff/status`). |
| **4. Memoria** | **Memoria de corto plazo** (historial de contexto de la sesión actual) complementada con **memoria de notas** (`notas.md`). | Los issues de mantenimiento de software son sesiones acotadas. El historial preserva los pasos recientes dentro de la ventana de contexto. La memoria de notas (`anotar` y `leer_notas`) permite condensar hipótesis intermedias sin saturar la ventana de contexto del LLM con observaciones repetitivas (Koenigstein, 2026). |
| **5. Coordinación** | **Por gestor** (planificador) + **Actor-Crítico** (ejecutor y revisor de código de solo lectura). | Separa nítidamente la responsabilidad de proponer modificaciones de código de la responsabilidad de evaluar su calidad, seguridad y no-regresión (Albada, 2025). El revisor carece intencionalmente de la herramienta `editar_archivo` (mínimo privilegio), evitando sobreescrituras no autorizadas y detectando inyecciones indirectas. |
| **6. Rol humano** | **Revisor y Gobernador** en el circuito (*Human-in-the-loop*). | El agente propone soluciones y el crítico las pre-evalúa, pero la decisión de aprobar ediciones de código sensible y fusionar el Pull Request recae siempre en un humano del equipo. Esto mitiga riesgos de exceso de agencia (OWASP LLM06) en fases tempranas de adopción. |
| **7. Control y Guardrails** | Contrato estructurado JSON, política de permisos por rol, rutas protegidas (`tests/`), presupuesto máximo de 15 pasos y 2 rondas. | Blindaje contra "la trampa del JSON frágil", bucles infinitos y costos desmedidos de API. Proteger `tests/` impide que el agente "arregle" las pruebas en lugar del código fuente. Las fallas de contrato y violaciones de política se devuelven al agente como observaciones para su autocorrección. |

---

## 2. Definición del Problema y Tareas Asignadas

El sistema agéntico se despliega para resolver tres incidencias reales sembradas en los módulos del Monolito Modular de **San Camilo en Línea**:

1. **Issue #01 (`issues/ISSUE-01.md`):** Duplicación de la comisión base fija en pedidos multipuesto dentro de `src/pedidos/comisiones.py`.
2. **Issue #02 (`issues/ISSUE-02.md`):** Exposición de productos agotados (`stock_disponible = 0`) en el catálogo visible dentro de `src/pedidos/catalogo.py`.
3. **Issue #03 (`issues/ISSUE-03.md`):** Desviación por redondeo de céntimos en liquidaciones a comerciantes en `src/pedidos/liquidacion.py`.

Cada issue cuenta con su especificación formal (observado, esperado y prueba de reproducción) y su respectiva prueba automatizada en `tests/` en estado inicial fallido (rojo).
