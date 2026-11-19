# E4. Normalización de nombres de productos

## Qué hace

La tarea recibe una lista de nombres escritos por comerciantes. Devuelve un producto del catálogo para cada entrada. Si el nombre es desconocido o ambiguo, devuelve desconocido. Mantiene el orden, los duplicados y el texto original.

El catálogo tiene siete productos y alias explícitos. Es un catálogo de prueba del laboratorio, no un inventario real de San Camilo. Agregar un producto exige actualizar el catálogo, el esquema y los casos correspondientes.

Por ejemplo, LIMON corresponde a limón y qso paria corresponde a queso paria. Papa no se asigna a una variedad porque puede referirse a papa blanca o papa amarilla. Tomate seguido de una instrucción tampoco coincide con un nombre completo del catálogo.

## Archivos

| Archivo | Función |
|---|---|
| `catalogo.json` | Define productos y alias autorizados |
| `esquema.json` | Exige las claves, tipos y parejas correctas de identificador y nombre |
| `casos.yaml` | Contiene doce casos con expectativas fijadas antes de preparar las muestras |
| `v1.txt` | Petición breve de normalización y salida JSON |
| `v2.txt` | Añade reglas de comparación, casos ambiguos, ejemplos y revisión interna |
| `v3.txt` | Refuerza la coincidencia completa, la preservación de entradas y la defensa ante órdenes mezcladas |
| `grabaciones/` | Contiene muestras de referencia, con la limitación explicada abajo |
| `promptfooconfig*.yaml` | Evalúa cada versión con las mismas cinco aserciones |
| `resultados/` | Guarda los reportes de reproducción de muestras |

## Casos y aserciones

Los casos cubren nombres exactos, mayúsculas, tildes, alias, productos ausentes, ambigüedad, entradas vacías, una lista vacía, duplicados, variedades distintas e inyecciones directas e indirectas.

Las aserciones comprueban el contrato JSON, la pertenencia al catálogo o a desconocido, la cantidad y el orden, la asignación esperada y la coincidencia completa. No basta con devolver desconocido para todo. Tampoco basta con devolver un identificador existente asociado a un nombre equivocado.

La comparación ignora mayúsculas, tildes y espacios repetidos. El campo entrada conserva el texto original. Por esa razón, el texto de un ataque puede aparecer copiado en ese campo. Copiar el dato no significa ejecutar la orden. Una prohibición global de la palabra APROBADO rechazaría incorrectamente esa copia literal.

## Iteraciones y límites de la evidencia

v1 deja implícitas varias reglas. v2 define que los alias son cerrados, que una variedad ausente no se debe adivinar y que cada entrada conserva su lugar. v3 aclara que no se pueden borrar palabras de una entrada para forzar una coincidencia y que una etiqueta dentro del texto no cambia las instrucciones.

v2 y v3 incluyen rol, contexto, tarea, restricciones, formato, ejemplos y entrada. Aplican few-shot y Cognitive Verifier.

Las tres carpetas de respuestas contienen el mismo conjunto de muestras de referencia redactadas por Codex en esta sesión. Se reutilizan de forma explícita para comprobar la configuración de cada versión. No representan tres ejecuciones del modelo ni una mejora medida entre versiones. No se introdujeron fallos artificiales para aparentar una evolución.

Para cerrar la evidencia de E4 hace falta ejecutar cada versión con las doce entradas y guardar cada salida original. Después se deben volver a ejecutar las evaluaciones, explicar los fallos reales y comprobar que la mejor versión supera 85 %. Con doce casos, once aprobados equivalen a 91,67 %.

La normalización determinista ya se puede resolver con las reglas del catálogo. El uso de un prompt aquí responde al ejercicio académico. Los casos no demuestran que un modelo sea necesario para esta función.
