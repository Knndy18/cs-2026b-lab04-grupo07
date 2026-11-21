<!-- Enlace oficial a prompts/bitacora-ia.md -->
# Bitácora de Uso de IA y Experimento de No Determinismo (E7)

> El documento completo y versionado se encuentra en [`prompts/bitacora-ia.md`](prompts/bitacora-ia.md).

Consulte [prompts/bitacora-ia.md](prompts/bitacora-ia.md) para revisar:
1. Tabla de interacciones con la IA generativa (incluyendo sugerencias rechazadas con evidencia técnica).
2. Protocolo del experimento de no determinismo ejecutado 3 veces sobre los casos H1, H6 y H8.
3. Análisis de 5 líneas sobre variabilidad probabilística, fixtures grabadas y robustez del contrato JSON Schema.


---

## Interacciones del Asistente de IA en Práctica 10: Tareas E4 a E6 (Nagin)

1. **Corrección de SyntaxError en `herramientas.py` detectado por pytest:** Durante la ejecución inicial de `python -m pytest -q agentes/pruebas_agente`, la suite abortó en la fase de colección debido a `SyntaxError: f-string expression part cannot include a backslash` en la línea 48 de `herramientas.py`. El error fue detectado directamente por el ejecutor de pruebas bajo Python 3.10; se resolvió abstrayendo la conversión de rutas a una variable intermedia (`rel_posix = str(rel).replace('\\', '/')`) antes de interpolarla en la f-string.
2. **Diseño e implementación de `mapa_repo()` con AST (E4):** Se implementó la introspección estática de código recorriendo el sandbox con `ast.parse` para extraer jerarquía de carpetas, clases y signaturas de funciones con `ast.unparse`. Se incluyó manejo defensivo contra `SyntaxError` (devolviendo el error formateado como texto explicativo sin propagar excepción) y truncamiento de salida a un máximo de 4,000 caracteres para evitar saturación de ventana de contexto.
3. **Memoria de notas o pizarra (`anotar` y `leer_notas` en `notas.md`):** Se implementó la memoria externa de notas garantizando numeración secuencial de hipótesis y validación estricta de cadenas no vacías. En la prueba unitaria `test_memoria_notas_validacion_texto_vacio` se verificó que entradas inválidas (`""`, `"   "`, `None`) devuelven mensaje de error sin corromper el archivo.
4. **Resolución de Issue #03 mediante agente ReAct:** Se generó la trayectoria grabada `ejecutor_issue_03.json` que utiliza `mapa_repo`, anota su hipótesis en `notas.md`, consulta la memoria con `leer_notas` y corrige el descuadre contable en `src/pedidos/liquidacion.py` deduciendo directamente la retención redondeada (`total_bruto - retencion`), logrando que la prueba `test_liquidacion_semanal_redondeo_exacto_centimos` pase al 100%.
5. **Detección de error por el Revisor Crítico en bucle Actor-Crítico (E5 - Issue #02):** En la Variante B del Issue #02 (`src/pedidos/catalogo.py`), el agente ejecutor en la Ronda 1 propuso una corrección simple (`p.activo and p.stock_disponible > 0`). El revisor crítico detectó que la solución omitía el caso de inventario nulo (`stock_disponible is None`), emitiendo `CAMBIOS SOLICITADOS` por riesgo de `TypeError` en producción. En la Ronda 2, el ejecutor incorporó la comprobación defensiva completa y el revisor emitió `APROBADO`.
6. **Implementación y verificación de Humano en el Circuito (`aprobar_edicion` en E6):** Se programó la compuerta de autorización en `agente/politica.py` que solicita confirmación por consola mediante `¿Aprobar edición? (s/n): `, repitiendo ante entradas inválidas ("x", "", "si"). Se verificó mediante `test_agente_edicion_rechazada_no_modifica_archivo` con `monkeypatch` que una respuesta "n" bloquea la acción con `"El revisor humano rechazó la edición"` y garantiza que el archivo en disco permanezca intacto.
