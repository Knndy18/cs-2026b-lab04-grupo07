# Trabajo de Nagin para el Laboratorio 09

## De quién depende el cierre

Diego ya publicó la base que permite trabajar: esquema, casos, v1 y ocho respuestas. No había un reporte de ejecución guardado. La reproducción realizada en esta revisión confirma cero casos aprobados de ocho.

E1 todavía necesita confirmar las seis historias reales del backlog. El conjunto publicado tiene cinco historias normales, dos no INVEST y una adversaria. Se conservó para no alterar la comparación.

Diego también tiene pendiente E8: integrar los resultados definitivos en el README, incorporar el gráfico y las lecciones, revisar la fusión del trabajo y crear la etiqueta v0.9-prompts. Esa etiqueta no estaba en el repositorio revisado. No se puede verificar desde el repositorio si se entregó algo en el Aula Virtual.

Kennedy debe contrastar sus defensas de v3.1 con la v3 que finalmente se evalúe y revisar el CI. El workflow actual usa `|| true` al ejecutar promptfoo, por lo que una evaluación fallida no detiene el trabajo. No se cambió su entregable E7 en esta revisión.

Nagin puede avanzar con E3 y E4 sin esperar otra implementación. Para cerrar esos entregables todavía hacen falta las ejecuciones reales del asistente con cada prompt y cada caso. Las muestras incluidas no sustituyen esa evidencia.

## Qué se preparó

- Dos versiones nuevas para criterios, con formato JSON, revisión de INVEST, ejemplos y defensas ante instrucciones dentro de las historias.
- Una auditoría de los evaluadores, con pruebas que comprueban respuestas incorrectas que antes podían pasar y palabras válidas que podían rechazarse.
- La tarea de normalización con un catálogo de siete productos, un contrato estricto, doce casos y tres versiones del prompt.
- Seis configuraciones reproducibles de promptfoo, reportes completos, un resumen por caso y una comparación de regresiones.
- Un registro que distingue respuestas heredadas y muestras sintéticas, con huellas de integridad.

## Qué se comprobó

Las pruebas de evaluadores y de la integración de criterios pasaron. En promptfoo, v1 de criterios obtuvo 0 de 8. Las muestras de criterios v2 y v3 obtuvieron 8 de 8. Las muestras de normalización obtuvieron 12 de 12 en cada configuración.

Estos porcentajes describen archivos guardados. No son una medición de mejora del modelo. En normalización se reutilizó expresamente el mismo conjunto de respuestas y no se inventaron fallos para simular una progresión.

## Archivos para revisar

- [Explicación de E3](criterios/iteraciones.md)
- [Explicación de E4](normalizacion/README.md)
- [Comandos de evaluación](README-evaluacion.md)
- [Resultados de las muestras](resultados.md)
- [Procedencia e integridad](procedencia.json)

## Publicación

Los cambios se prepararon en la rama `feat/nagin-lab09-e3-e4`. La cuenta NaginCarferC completó la autorización de GitHub CLI y se verificó que tiene permiso para escribir en el repositorio. La publicación corresponde a esa cuenta.

El trabajo se presenta para revisión como borrador. No se creó la etiqueta de entrega final porque las capturas experimentales y el cierre del equipo siguen pendientes.

## Límite de las pruebas generales

La suite completa se detiene al importar `simular` desde `fitness.rendimiento`. Es un fallo previo de `tests/test_fitness.py`, fuera de E3 y E4. Existe el pull request 6 sobre esa compatibilidad. Las 21 pruebas de evaluadores e integración de criterios pasan.

La versión fija de promptfoo usada requiere Node.js 22.22 o posterior. El workflow previo de Kennedy utiliza Node.js 20, por lo que también necesita actualizar esa versión antes de adoptar esta configuración en CI.
