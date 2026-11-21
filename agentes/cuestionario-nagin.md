# Cuestionario de la Práctica 10: Sistemas Agénticos (Nagin - E4 a E6)

Respuestas basadas en los fundamentos teóricos de Albada (2025) y Koenigstein (2026), y respaldadas con métricas empíricas obtenidas de las trazas del repositorio de **San Camilo en Línea**.

---

### Pregunta 4: ¿Qué es un contrato estructurado y qué pasa en nuestro agente cuando el modelo lo incumple? Incluye un ejemplo real y explica el flujo.

Un contrato estructurado es un esquema formal de validación sintáctica y semántica (implementado en `agente/contrato.py` con `validar_decision`) que garantiza que cada salida del modelo cumpla estrictamente con el protocolo JSON requerido antes de interactuar con el entorno.
En nuestro sistema, la decisión debe contener un `pensamiento` no vacío, exactamente una clave entre `accion` o `final`, argumentos `args` en formato diccionario y herramientas pertenecientes al catálogo conocido (`HERRAMIENTAS_CATALOGO`).
Cuando el modelo incumple estas reglas (por ejemplo, en nuestra prueba `test_contrato_decisiones_invalidas_propias` con `{"pensamiento": "x", "accion": "leer_archivo", "final": "y"}`, rechazada con `"debe incluir 'accion' o 'final', pero no ambos"`), la máquina de estados intercepta la falla en `ValidandoContrato`.
El núcleo no aborta la ejecución ni propaga excepciones al sistema: en su lugar, transiciona a `CONTRATO_INVALIDO`, registra el evento en la traza marcándolo como `bloqueada=True`, y sintetiza una respuesta de retroalimentación: `f"ERROR DE CONTRATO: {motivo}. Responda solo con el JSON del protocolo."`.
Esta advertencia se inyecta en el historial conversacional como una observación con rol de usuario (`role: "user"`), retornando el control a la fase `Decidiendo` en el siguiente paso para que el modelo rectifique su salida de forma autónoma.
Este mecanismo defensivo previene la "trampa del JSON frágil" descrita por Koenigstein (2026, cap. 5), blindando al agente contra alucinaciones de formato sin quebrar el ciclo ReAct.

---

### Pregunta 5: ¿Qué tipo de memoria agregamos en E4 (notas/pizarra, y en qué categoría de la Tabla 6 cae) y qué efecto tuvo en pasos y contexto?

En E4 incorporamos una memoria de notas o pizarra mediante las herramientas `anotar(texto)` y `leer_notas()`, las cuales operan persistiendo apuntes e hipótesis en el archivo `notas.md` dentro del sandbox del repositorio.
Según la taxonomía de Koenigstein (2026, cap. 10) y Albada (2025, cap. 6) sintetizada en la Tabla 6 de la guía, esta memoria pertenece a la categoría de **Notas o pizarra** (*scratchpad/blackboard*), un mecanismo de persistencia externa deliberativa para registrar hipótesis y deducciones intermedias durante la sesión.
Al medir el impacto cuantitativo frente a la línea base de E2 (Issue #01) documentado en `agentes/e4-herramienta-memoria.md`, observamos un incremento de 9 a 10 pasos totales y de 8 a 9 acciones ejecutadas, atribuible a los turnos dedicados a persistir y consultar la memoria de notas.
El contexto acumulado en la traza se incrementó de 6,685 a 8,183 caracteres (+22.4%), dado que la herramienta `mapa_repo` inyectó el árbol de clases y signaturas de `src/pedidos` y `leer_notas` devolvió la hipótesis registrada.
Pese a que no hubo reducción numérica de caracteres ni de pasos para este issue acotado, la memoria aportó un beneficio cualitativo sustancial: el agente resolvió el fallo contable de `src/pedidos/liquidacion.py` de forma determinista y sin desvíos, reduciendo las acciones bloqueadas de 1 (bloqueo de script malicioso en E2) a 0 en E4.

---

### Pregunta 6: Según E5, ¿compensó el bucle actor-crítico su costo adicional? Relaciona tu respuesta con el principio de parsimonia.

De acuerdo con los datos medidos en `agentes/e5-coordinacion.md`, la variante actor-crítico demandó 2 rondas, 17 acciones a herramientas, 22 pasos acumulados y 21,512 caracteres de contexto, frente a 1 ronda, 7 acciones, 8 pasos y 6,559 caracteres del agente único (un incremento de 3.28x en contexto).
El principio de parsimonia en sistemas multiagente (Albada, 2025, cap. 8) exige comenzar siempre con el diseño más simple y añadir más agentes únicamente cuando la complejidad o el riesgo del dominio justifiquen fehacientemente el costo extra de computación y latencia.
En el Issue #02, el agente único logró hacer pasar la prueba unitaria inmediata con un costo mínimo, pero exhibió miopía de confirmación al omitir el escenario de inventario nulo (`stock_disponible is None`), defecto que hubiera desencadenado un error en tiempo de ejecución (`TypeError`) al atender datos no inicializados.
El revisor crítico de solo lectura inspeccionó el cambio, detectó esta omisión en la primera ronda y emitió `CAMBIOS SOLICITADOS`, forzando al ejecutor en la segunda ronda a implementar un filtrado defensivo robusto y a remover los comentarios de error del código fuente.
Por consiguiente, aunque para tareas puramente sintácticas o cosméticas la parsimonia desaconseja el multiagente, en módulos con impacto en el catálogo y despacho del Mercado San Camilo el bucle actor-crítico **sí compensó con creces su costo adicional**, pues previno una falla silenciosa en producción que el agente único pasó por alto.
