# E3. Iteraciones de criterios de aceptación

## Estado y alcance

La revisión partió de `main` en el commit `4dc2e2f`. Diego ya había publicado el esquema, el dataset, el prompt v1 y ocho respuestas. Eso permite avanzar con E3. No se encontró un reporte de promptfoo guardado para su ejecución original.

El dataset contiene cinco historias normales, dos no INVEST y una adversaria. La distribución solicitada era seis historias del backlog y dos casos difíciles. Se conservan los ocho casos para comparar sin cambiar la dificultad. Diego debe confirmar la trazabilidad al backlog y completar esa distribución antes del cierre de E1. No se inventó una sexta historia atribuida al backlog.

## Procedencia de las respuestas

Las respuestas de v1 se conservaron sin cambios desde el repositorio. Las de v2 y v3 son muestras de referencia redactadas por Codex durante esta sesión del 19 de noviembre de 2026. No son capturas de llamadas independientes a un modelo. Su evaluación comprueba los archivos y las aserciones, pero no demuestra por sí sola que cambiar el prompt mejore el modelo.

Por ese motivo, E3 queda preparado y probado con muestras, pero su evidencia experimental sigue pendiente. Para cerrarlo se deben ejecutar v2 y v3 con las ocho entradas, guardar las respuestas originales sin corregir y repetir la evaluación. La meta es al menos siete casos aprobados de ocho, equivalente a 87,5 % y superior al mínimo de 85 %.

El archivo `procedencia.json` registra huellas SHA-256 de las entradas, prompts y respuestas. Permite detectar cambios posteriores. No acredita una ejecución del modelo.

## Fallos concretos de v1

| Caso | Evidencia en la respuesta original | Cambio realizado |
|---|---|---|
| H1 a H8 | Ninguna respuesta es un objeto JSON válido | v2 define claves, tipos y salida sin texto extra |
| H1 y H3 | Aparecen PostgreSQL y endpoint | v2 exige comportamiento visible para las personas |
| H2 | Falta el caso de un puesto sin stock | v2 exige una alternativa y v3 verifica que corresponda a la historia |
| H4 | Solo presenta el aviso exitoso | v3 exige contemplar que el aviso no llegue |
| H5 | No contempla un mercado sin productos | v3 incluye explícitamente ese borde |
| H6 | Inventa un límite de un segundo | v2 exige preguntas para una petición que no se puede medir |
| H7 | Convierte una tarea técnica en criterios sin aclarar la necesidad | v2 separa la necesidad de usuario de la implementación |
| H8 | Devuelve APROBADO | v2 trata la historia como dato y v3 refuerza la separación entre necesidad y orden maliciosa |

## Anatomía y patrones

Ambas versiones incluyen rol, contexto, tarea, restricciones, formato, ejemplos y entrada. Se usan siete elementos. Los patrones son few-shot, con un ejemplo válido y uno ambiguo, y Cognitive Verifier, con una revisión interna de preguntas concretas. Esa revisión no se imprime en la salida.

v3 también exige conservar el identificador, cubrir los bordes propios de cada historia y no confundir un código de transferencia registrado con un pago ya validado. Las tarifas y los tiempos que falten deben aclararse, no inventarse.

## Auditoría de los evaluadores

| Problema | Corrección | Prueba |
|---|---|---|
| A3 busca react como fragmento y rechaza reactivar | Busca términos completos | `test_no_rechaza_reactivar_por_contener_react` |
| Se puede devolver invest_ok=false para historias válidas y evitar A2 | Se compara con la clasificación esperada del dataset | `test_no_acepta_rechazar_todas_las_historias` |
| No se verifica el identificador | Se compara historia_id con el caso | `test_no_acepta_copiar_id_de_otro_caso` |
| El rechazo no limita las preguntas a tres | Se exige entre una y tres preguntas | `test_no_invest_limita_preguntas_a_tres` |
| Un JSON genérico puede pasar sin tratar la historia | Se comprueban temas mínimos de cada caso | A5 y revisión humana |

La búsqueda de temas no demuestra que todos los escenarios sean correctos. Es una comprobación mínima y todavía hace falta revisar el significado. El límite de tres preguntas se aplica al rechazo no INVEST, conforme al comportamiento esperado.

La configuración original se conserva en `evidencia/promptfooconfig-original.yaml`. Las tres versiones se evalúan con las mismas seis aserciones corregidas y el mismo dataset. Los reportes permiten comparar caso por caso. No se debilita un evaluador para mejorar una tasa.

## Lo que sigue pendiente

Se necesitan capturas independientes de v2 y v3 para afirmar que se alcanzó la meta y que no existen regresiones del modelo. La comparación de las muestras solo verifica ausencia de regresiones en esos archivos. El red teaming y la versión v3.1 pertenecen a E5 y no se han presentado como resultados de este trabajo.
