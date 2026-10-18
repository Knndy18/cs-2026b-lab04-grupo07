# Respuestas al Cuestionario – Caso: San Camilo en Línea

---

# Laboratorio 04

## 1. ¿Por qué se afirma que una decisión arquitectónica es aquella "costosa de cambiar"? Dé un ejemplo de su caso.

Una decisión arquitectónica es "costosa de cambiar" porque impacta las bases estructurales, la organización del código, las dependencias de infraestructura y la forma en que interactúan los módulos del sistema. Cambiarla en etapas avanzadas no implica solo modificar unas pocas líneas de código, sino reescribir componentes enteros, migrar datos y reconfigurar la infraestructura.

**Ejemplo del caso San Camilo en Línea:** La elección de **PostgreSQL** como almacenamiento principal en lugar de una base de datos NoSQL (`ADR-002`). Si a mitad del desarrollo se intentara cambiar a MongoDB, se tendría que rediseñar el modelo relacional de carritos multi-puesto (`pedido_items`), reescribir las transacciones ACID que garantizan la integridad de los pagos/pedidos y modificar todas las consultas de auditoría para la resolución de reclamos (`R-06`, `R-07`), lo que echaría por tierra la restricción de tiempo de **1 mes** (`R-01`).

---

## 2. ¿Cuál es la diferencia entre un requisito funcional y un atributo de calidad? ¿Por qué los atributos de calidad influyen más en la arquitectura?

* **Requisito Funcional (RF):** Define **qué** hace el sistema o qué acción específica debe ejecutar (ej.: `RF-04`: *"El cliente registra la constancia o referencia del pago con Yape"*).

* **Atributo de Calidad (QA):** Define **cómo de bien** debe operar el sistema en términos de propiedades no funcionales como disponibilidad, rendimiento o modificabilidad (ej.: `QA-02`: *"Los pedidos confirmados no deben perderse aunque WhatsApp no responda"*).

**¿Por qué influyen más en la arquitectura?** Los requisitos funcionales generalmente pueden implementarse agregando nuevas vistas, controladores o algoritmos dentro de casi cualquier estructura básica. Sin embargo, los atributos de calidad (como soportar consultas masivas en picos de demanda o aislar fallas de servicios externos) dictan la elección del estilo arquitectónico (Monolito Modular vs. Microservicios), la estrategia de persistencia y los patrones de integración.

---

## 3. Reescriba el requisito "el sistema debe ser seguro" como un escenario de atributo de calidad de seis partes.

Para el atributo de **Seguridad y Autorización por Rol (`QA-05`)** en San Camilo en Línea:

1. **Fuente del estímulo:** Comerciante autenticado de un puesto específico.

2. **Estímulo:** Intento deliberado o accidental de editar o eliminar productos/precios pertenecientes a otro puesto del mercado.

3. **Artefacto:** Módulo de Catálogo / API de Productos y middleware de autorización por rol.

4. **Entorno:** Operación normal del sistema desde un dispositivo móvil.

5. **Respuesta:** El sistema valida la pertenencia del recurso (`puesto_id`), bloquea el acceso no autorizado con un código HTTP `403 Forbidden` y registra el intento no autorizado en la auditoría.

6. **Medida de la respuesta:** 100% de los intentos no autorizados rechazados (0 datos de otros puestos modificados).

---

## 4. Compare el monolito modular y los microservicios en términos de costo, modificabilidad y complejidad operativa. ¿En qué momento convendría migrar de uno a otro?

| Criterio                  | Monolito Modular (`ADR-001`)                                                                                                          | Microservicios                                                                                                 |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| **Costo**                 | **Bajo:** Despliegue en un único servidor VPS de bajo costo (`R-03`), ideal para presupuestos acotados.                               | **Alto:** Múltiples contenedores/nodos, orquestadores, mayor consumo de recursos e infraestructura en la nube. |
| **Modificabilidad**       | **Media/Alta:** Interfaces claras in-process entre módulos (Catalogo, Pedidos, Pagos) que permiten cambios en $\le 2$ días (`QA-04`). | **Muy Alta:** Cada servicio se modifica, compila, despliega y escala de forma $100%$ independiente.            |
| **Complejidad Operativa** | **Baja:** Un solo pipeline de despliegue, monitoreo centralizado y depuración directa.                                                | **Muy Alta:** Latencia de red, consistencia eventual, transacciones distribuidas y tracing distribuido.        |

**¿Cuándo convendría migrar?** Convendría migrar de Monolito Modular a Microservicios si el sistema experimenta un crecimiento masivo donde un módulo específico (ej.: el motor de seguimiento e itinerarios de Repartidores en tiempo real) requiera un escalado independiente que ponga en riesgo la capacidad del VPS único, o cuando el equipo de desarrollo crezca a múltiples sub-equipos trabajando de forma autónoma.

---

## 5. ¿Qué ventajas ofrece Diagram as Code frente a herramientas de dibujo como PowerPoint? Mencione al menos tres.

1. **Control de Versiones y Trazabilidad (Git):** Los diagramas se almacenan como código (ej. PlantUML o Mermaid), permitiendo ver un `git diff` de los cambios arquitectónicos junto con el código fuente.

2. **Mantenibilidad Automática:** Modificar una relación entre módulos implica editar un texto breve; la herramienta re-renderiza todo el diagrama sin tener que reorganizar manualmente cajas, flechas y colores.

3. **Consistencia Visual e Integración en Documentación:** Mantiene un estándar visual uniforme y se integra automáticamente en los archivos Markdown del repositorio y pipelines de CI/CD.

---

## 6. ¿Qué elementos debe contener un ADR y por qué es importante registrar también las alternativas descartadas?

Un **ADR (Architecture Decision Record)** debe contener:

* **Título y Estado:** Nombre descriptivo y estado (Aceptado, Rechazado, Superado).

* **Contexto:** El problema operativo, los drivers de negocio y las restricciones que motivan la decisión.

* **Decisión:** La solución técnica adoptada explícitamente.

* **Consecuencias:** Efectos positivos, riesgos/inconvenientes y sus correspondientes estrategias de mitigación.

**Importancia de registrar alternativas descartadas:** Evita reconsiderar opciones que ya fueron evaluadas y rechazadas, sirve de memoria técnica para nuevos desarrolladores que se sumen al equipo y demuestra la rigurosidad técnica al explicar los *trade-offs* de por qué una solución no era viable para las restricciones del proyecto.

---

## 7. Describa un caso de esta práctica en el que la IA haya generado una propuesta incorrecta o sesgada. ¿Cómo lo detectaron?

Al solicitar las alternativas de arquitectura backend mediante el Prompt 1, la IA recomendó una arquitectura basada en **Microservicios con orquestación en Kubernetes y servicios Serverless**.

**Cómo se detectó:** Durante la revisión de trazabilidad contra el documento `drivers.md`, el equipo identificó que esa solución violaba directamente la restricción de plazo `R-01` (1 mes para salir a producción), la restricción de equipo `R-02` (máximo 3 developers) y la restricción presupuestal `R-03` (un único servidor VPS económico). Mediante el Prompt 2 (crítica adversarial), se forzó a la IA a admitir la sobrecomplejidad de su recomendación y se corrigió hacia un **Monolito Modular**.

---

## 8. ¿Qué riesgos éticos y de confidencialidad existen al usar asistentes de IA para diseñar la arquitectura de un sistema real?

1. **Fuga de Información Confidencial (Data Leakage):** Enviar variables de entorno, esquemas de bases de datos con datos reales de comerciantes/clientes o claves privadas a modelos de IA públicos puede exponer datos protegidos a terceros o utilizarlos para reentrenar modelos SaaS.

2. **Vulnerabilidades de Código/Configuración:** Copiar ciegamente reglas de seguridad o fragmentos de infraestructura sugeridos por IA puede introducir agujeros de seguridad (como endpoints desprotegidos o la exposición de credenciales) si no son revisados por un profesional humano.

3. **Infracción de Licencias y Propiedad Intelectual:** La IA puede generar patrones o código copiados directamente de repositorios con licencias restrictivas sin la debida atribución.

---

# Laboratorio 05

---

## 1. ¿Qué diferencia hay entre el diseño arquitectónico del Laboratorio 04 y el diseño detallado de este laboratorio? Dé un ejemplo de su caso.

* **Diseño Arquitectónico (Lab 04):** Se enfoca en la visión de alto nivel del sistema: define el estilo general (Monolito Modular, `ADR-001`), los grandes subsistemas/módulos, las tecnologías de persistencia (`ADR-002`), los mecanismos de despliegue y cómo se satisfacen los atributos de calidad (`QA-01` a `QA-05`). No se preocupa por firmas de métodos, tipos de datos primitivos ni algoritmos internos.
* **Diseño Detallado (Lab 05):** Desciende al nivel micro-estructural y de comportamiento interno: especifica clases concretas, visibilidad de atributos (`private`, `public`), tipos de retorno, excepciones, contratos de interfaces (puertos), secuencia exacta de invocación de mensajes y máquinas de estados de entidades.

**Ejemplo del caso San Camilo en Línea:**
* En el Lab 04, el módulo `Pedidos` se definió simplemente como una caja funcional responsable del ciclo de vida de los pedidos que interactúa conceptualmente con `Pagos` y `PostgreSQL`.
* En el Lab 05, ese módulo se descompone en clases concretas (`PedidoGlobal`, `PedidoPuesto`, `ItemPedido`), con métodos como `agregar_item(producto, cantidad)`, validaciones de excepciones de stock en `reservar_stock(cantidad)`, la definición del puerto `PasarelaPago` con su método `verificar_pago(monto, referencia) -> Pago`, y las transiciones válidas de la máquina de estados.

---

## 2. ¿Cuándo usaría composición y cuándo agregación? Justifique con dos relaciones de su diagrama de clases.

* **Composición (`*--`):** Se utiliza cuando existe una relación de pertenencia existencial estricta ("todo-parte"). Las partes no tienen sentido ni ciclo de vida independiente del todo; si el objeto contenedor se destruye o cancela, sus partes asociadas desaparecen con él.
* **Agregación (`o--`):** Se utiliza cuando una clase contiene o hace referencia a otra, pero ambas poseen ciclos de vida independientes ("tiene un"). Si el contenedor desaparece, el objeto contenido sigue existiendo en el sistema.

**Justificación con relaciones del diagrama de clases (`clases.puml`):**
1. **Composición: `PedidoGlobal` y `PedidoPuesto` (`PedidoGlobal *-- PedidoPuesto`):** Un `PedidoPuesto` representa la fracción de una orden asignada a un puesto específico dentro de una compra multi-puesto. No puede existir un `PedidoPuesto` huérfano en el sistema sin un `PedidoGlobal` que lo agrupe y le dé origen financiero; si el pedido global se descarta o elimina, sus subdivisiones por puesto pierden su razón de ser.
2. **Agregación / Asociación débil: `PedidoPuesto` y `Puesto` (`PedidoPuesto --> Puesto`):** Un pedido por puesto referencia al `Puesto` comercial del mercado que debe despachar los productos. Sin embargo, el puesto comercial existe independientemente de si tiene o no pedidos asignados. Si un pedido se cancela o finaliza, la entidad `Puesto` permanece intacta en el catálogo del mercado.

---

## 3. ¿Por qué en el diagrama de clases se modela la pasarela de pagos (o el servicio externo de su caso) como interfaz y no como superclase? Relaciónelo con el ADR-001.

Se modela como interfaz (puerto `PasarelaPago`) aplicando el **Principio de Inversión de Dependencias (DIP)** de la arquitectura hexagonal / puertos y adaptadores:

1. **Desacoplamiento y polimorfismo puro:** Una superclase abstracta suele implicar jerarquías de herencia y compartir estado o lógica de negocio base, mientras que una interfaz define únicamente un contrato puro (`verificar_pago(monto, referencia) -> Pago`).
2. **Relación con ADR-001 (Monolito Modular):** En el ADR-001 se estableció que el núcleo del dominio de `Pedidos` no debe conocer ni acoplarse a detalles técnicos de proveedores externos. Modelar `PasarelaPago` como una interfaz permite que `YapeAdapter` resida en la capa de `infraestructura.pagos` implementando dicho puerto. Si mañana el mercado decide incorporar Plin, POS físico o tarjeta bancaria (cumpliendo el driver de modificabilidad `QA-04`), solo se crea un nuevo adaptador (`PlinAdapter`) sin modificar una sola línea de código del módulo `pedidos`.

---

## 4. Explique la regla C1 y muestre un mensaje de su diagrama de secuencia que la incumplía antes de corregirlo.

* **Explicación de la Regla C1 (Consistencia de Nomenclatura y Métodos):** Establece que toda operación, mensaje o método invocado en un diagrama dinámico (como el diagrama de secuencia o actividades) debe corresponder exactamente con el nombre, signatura y entidad receptora definida formalmente en el diagrama estructural de clases.

* **Mensaje que incumplía la regla antes de corregirse:**
  * **Invocación inicial en el diagrama de secuencia:**
    ```text
    S -> PG : pagarPedido(referenciaYape)
    ```
  * **Problema:** En el diagrama de clases (`clases.puml`), la entidad `PedidoGlobal` no posee ningún método llamado `pagarPedido()`. El procesamiento y validación del pago es una responsabilidad del servicio de aplicación (`ServicioPedidos.procesar_pago_yape()`), mientras que en `PedidoGlobal` la operación real definida para reflejar el éxito del pago es `confirmar()` y en `PedidoPuesto` es `registrarPago(pago)`.
  * **Corrección aplicada:** Se ajustó la secuencia para que `ServicioPedidos` invoque a la pasarela, actualice la orden mediante `PG.confirmar()` y luego llame a `PP.registrarPago(pago)` y `PP.cambiar_estado(PAGADO)`, respetando exactamente las signaturas del diagrama de clases.

---

## 5. ¿Cómo se derivan casos de prueba a partir de un diagrama de máquina de estados? Indique cuántas pruebas mínimas requiere su diagrama.

Los casos de prueba se derivan a partir de la cobertura de la máquina de estados siguiendo dos niveles de rigor:
1. **Cobertura de estados (State Coverage):** Garantizar que cada estado posible sea alcanzado al menos una vez por alguna prueba.
2. **Cobertura de transiciones (Transition Coverage 0-switch):** Diseñar un caso de prueba para cada transición válida (disparador + condición de guardia $\to$ estado destino) y casos de prueba negativos para verificar que las transiciones inválidas sean rechazadas con error.

**Cálculo de pruebas mínimas para `estados-pedido.mmd`:**
El ciclo de vida de `PedidoPuesto` cuenta con **8 estados** (`BORRADOR`, `PAGO_PENDIENTE`, `PAGADO`, `EN_PREPARACION`, `LISTO`, `RECOGIDO`, `ENTREGADO`, `RECHAZADO`):

* **Transiciones válidas (casos positivos mínimos):**
  1. `[*] -> BORRADOR` (evento: `agregarItem()`)
  2. `BORRADOR -> PAGO_PENDIENTE` (evento: `cambiarEstado()` con guardia `pedido global confirmado`)
  3. `PAGO_PENDIENTE -> PAGADO` (evento: `registrarPago()` con guardia `pago aprobado`)
  4. `PAGO_PENDIENTE -> RECHAZADO` (evento: `cambiarEstado()` con guardia `pago fallido/expirado`)
  5. `PAGADO -> EN_PREPARACION` (evento: `cambiarEstado()` con guardia `comerciante acepta`)
  6. `EN_PREPARACION -> LISTO` (evento: `cambiarEstado()` con guardia `producto empaquetado`)
  7. `LISTO -> RECOGIDO` (evento: `cambiarEstado()` con guardia `repartidor recoge`)
  8. `RECOGIDO -> ENTREGADO` (evento: `cambiarEstado()` con guardia `repartidor entrega`)
  9. `ENTREGADO -> [*]` (finalización exitosa)
  10. `RECHAZADO -> [*]` (finalización por cancelación)

* **Pruebas mínimas:**
  * **Pruebas positivas (caminos felices y alternativos):** Se requieren como mínimo **2 pruebas de extremo a extremo** para cubrir todas las transiciones válidas:
    * *CP-01 (Camino exitoso completo):* `BORRADOR -> PAGO_PENDIENTE -> PAGADO -> EN_PREPARACION -> LISTO -> RECOGIDO -> ENTREGADO`.
    * *CP-02 (Camino de rechazo):* `BORRADOR -> PAGO_PENDIENTE -> RECHAZADO`.
  * **Pruebas de transición inválida (negativas mínimas):** Al menos **1 prueba** que intente una transición ilegal (ej.: pasar de `BORRADOR` directamente a `ENTREGADO` sin pago) verificando que el sistema arroje una excepción (`ValueError`).
  * **Total de pruebas mínimas requeridas:** **10 pruebas unitarias de transición** (o 3 casos de prueba integrales que cubran todas las transiciones y excepciones).

---

## 6. ¿Qué información del diagrama de diseño se perdió en la ingeniería inversa (E6) y por qué?

Al aplicar ingeniería inversa con `pyreverse` sobre el código fuente en `src/pedidos/models.py`, se identificaron **5 pérdidas principales de información semántica** respecto a `clases.puml`:

1. **Estereotipos y conceptos arquitectónicos:** Los estereotipos UML como `<<puerto>>`, `<<adaptador>>` y `<<servicio>>` desaparecieron. `pyreverse` trata todas las clases por igual en Python y no puede deducir la intención arquitectónica hexagonal de un `typing.Protocol`.
2. **Literales de Enumeraciones:** En `clases.puml` la enumeración `EstadoPedidoPuesto` lista explícitamente sus estados (`RECIBIDO`, `LISTO`, `RECHAZADO`, etc.). En el diagrama generado por `pyreverse`, la enumeración aparece como una clase ordinaria con un único campo genérico `name`.
3. **Multiplicidades y roles:** Las multiplicidades estrictas (`1`, `0..*`, `1..*`) y las etiquetas semánticas (`realiza >`, `contiene >`) no existen en el código de producción como metadatos explícitos, por lo que `pyreverse` solo dibuja flechas directas con el nombre del atributo.
4. **Dependencias de uso e inyección (`..>`):** Las relaciones de uso donde `ServicioPedidos` interactúa con los puertos inyectados en su constructor no fueron capturadas como dependencias formales.
5. **Separación de capas e implementaciones externas:** Los adaptadores de infraestructura (`YapeAdapter`, `WhatsAppAdapter`) no aparecieron en el diagrama invertido del módulo `pedidos`. En este caso, esto es una consecuencia positiva del aislamiento del módulo exigido en el ADR-001.

**¿Por qué se pierde?** Porque el código fuente expresa cómo se ejecuta la solución técnica en la sintaxis de un lenguaje particular (Python), mientras que el diagrama de diseño UML captura **intenciones de diseño, decisiones arquitectónicas y restricciones de modelado** que el compilador o parser no necesita conocer para ejecutar el código.

---

## 7. ¿Qué falso positivo detectó en la revisión de consistencia con IA? ¿Qué habría pasado si lo aceptaba sin verificar?

* **Falso positivo detectado:** Durante la auditoría de consistencia arquitectónica (Interacción 3 y 4 de la bitácora), la IA sugirió que para que el módulo `Notificaciones` supiera cuándo un pedido cambiaba de estado, debía agregarse una dependencia directa desde `notificaciones` hacia `pedidos` ("para que el notificador escuche directamente las entidades del pedido"). La IA marcó esto inicialmente como una "buena práctica de desacoplamiento por eventos".

* **¿Por qué era un falso positivo?** En el diagrama de paquetes, `pedidos` ya poseía una dependencia hacia `notificaciones` para solicitar el envío de mensajes. Si se aceptaba la sugerencia de la IA, se introducía una **dependencia cíclica bidireccional (`pedidos <--> notificaciones`)**, violando directamente la regla de consistencia **C4 (Sin dependencias cíclicas)** y los principios fundamentales del monolito modular del ADR-001.

* **¿Qué habría pasado si se aceptaba sin verificar?**
  1. Se habría acoplado fuertemente el ciclo de vida del dominio de pedidos con el servicio de mensajería externa.
  2. Habría generado bloqueos o dependencias circulares de importación en el código (`circular import error` en Python).
  3. Habría impedido que en el futuro el módulo de `Notificaciones` pudiera extraerse como un servicio independiente sin arrastrar dependencias del núcleo de pedidos.

---

## 8. Según Fowler, UML puede usarse como boceto, plano o lenguaje de programación. ¿Cuál de esos usos aplicó en este laboratorio y por qué es adecuado para un MVP de 1 mes?

En este laboratorio aplicamos UML fundamentalmente como **Plano (Blueprint)**, complementado con elementos de **Boceto (Sketch)**:

* **Por qué se usó como Plano:**
  1. Se definieron contratos exactos y rigurosos antes de implementar: atributos con tipos de datos (`UUID`, `Decimal`, `str`), métodos con sus parámetros, multiplicidades en las asociaciones y puertos (`Protocol`) que guían directamente la codificación.
  2. Sirvió de base para la generación asistida por IA del esqueleto de código en `src/pedidos/models.py` y para la verificación round-trip con ingeniería inversa.

* **Por qué es adecuado para un MVP de 1 mes (`R-01`):**
  1. **Evita la parálisis por análisis del "UML como lenguaje de programación" (Model-Driven Architecture / MDA):** Intentar que los diagramas generen el 100% del código ejecutable con algoritmos detallados consume semanas de configuración y herramientas costosas, inviable para un plazo de 30 días y un equipo de 3 desarrolladores (`R-02`).
  2. **Previene el caos del "UML como simple boceto informal":** Un simple boceto en servilleta o pizarra habría dejado abiertas ambigüedades críticas sobre cómo gestionar el pago único en pedidos multipuesto, cómo aislar Yape o cómo evitar dependencias cíclicas.
  3. **Alineación rápida del equipo:** Al servir como plano conceptual, los tres integrantes pudieron trabajar en paralelo (clases, secuencias, estados y paquetes) teniendo total claridad sobre las interfaces y responsabilidades antes de escribir código.

---

# Laboratorio 06

---

## 1. ¿Qué problema de los diagramas tradicionales de "cajas y flechas" resuelve el modelo C4? Dé un ejemplo de ambigüedad que haya evitado en su caso.

El modelo C4 resuelve la ambigüedad conceptual y la falta de abstracción de los diagramas informales de "cajas y flechas", donde no se distingue si una caja representa un servidor físico, un contenedor Docker, una aplicación web, un módulo de código o un sistema externo. Además, C4 elimina las flechas sin intención clara mediante un conjunto formal de abstracciones jerárquicas (zoom).

**Ejemplo evitado en San Camilo en Línea:** En un diagrama tradicional, se podría dibujar una caja llamada "WhatsApp" conectada a una llamada "API". Esto genera ambigüedad sobre si WhatsApp es un módulo que estamos programando dentro de nuestro servidor o un servicio de terceros. C4 evitó este problema al clasificarlo explícitamente como un **Sistema de Software Externo** (`softwareSystem "WhatsApp Business API" "Externo"`) en el Nivel 1 (Contexto), aclarando que está fuera del alcance de nuestro despliegue.

---

## 2. ¿Qué es un "contenedor" en C4 y por qué no equivale a un contenedor Docker? Indique un contenedor de su caso que no se ejecute en Docker.

En el modelo C4, un **contenedor** es cualquier aplicación ejecutable o almacén de datos que se despliega o ejecuta por separado para que el sistema funcione (por ejemplo: un sitio web, una API REST, una base de datos o un script ejecutable). No equivale a un contenedor Docker porque C4 describe la arquitectura lógica/de software y no la tecnología de virtualización de infraestructura.

**Ejemplo de contenedor no ejecutable en Docker:** La **Aplicación Web Progresiva (PWA React)**. Este contenedor se ejecuta directamente en el navegador web del dispositivo móvil o PC del cliente/comerciante (`Web Browser`), fuera del entorno Docker Compose del servidor VPS.

---

## 3. ¿Qué público y qué nivel de detalle tiene cada uno de los cuatro niveles de C4? ¿Por qué rara vez se dibuja el nivel 4 a mano?

- **Nivel 1 (Contexto del Sistema):** Muestra el sistema en el centro, los usuarios (personas) y las interacciones con sistemas externos. **Público:** Todos, incluyendo personal no técnico.

- **Nivel 2 (Contenedores):** Muestra las aplicaciones ejecutables y almacenes de datos, con sus tecnologías y protocolos de comunicación. **Público:** Arquitectos, desarrolladores y personal de operaciones.

- **Nivel 3 (Componentes):** Muestra los módulos internos y responsabilidades dentro de un contenedor específico (por ejemplo, los módulos de la API). **Público:** Desarrolladores y arquitectos.

- **Nivel 4 (Código):** Muestra los elementos de implementación como clases, interfaces y patrones (diagrama UML). **Público:** Desarrolladores.

**¿Por qué rara vez se dibuja el nivel 4 a mano?** Porque cambia con alta frecuencia a medida que se escribe código. Mantener diagramas de clases UML dibujados a mano se vuelve insostenible en proyectos reales. Es mucho más eficiente generarlos bajo demanda mediante ingeniería inversa (como `pyreverse` en el Lab 05) a partir del código fuente.

---

## 4. Compare la vista dinámica de C4 con el diagrama de secuencia UML de su flujo crítico. ¿Cuándo usaría cada una?

- **Vista Dinámica C4:** Describe la interacción a alto nivel entre contenedores o componentes mediante pasos numerados de un caso de uso (por ejemplo: PWA $\rightarrow$ Módulo Pedidos $\rightarrow$ Pasarela Yape). Omite detalles como activaciones de hilos, llamadas a métodos o condicionales detallados.

- **Diagrama de Secuencia UML:** Describe interacciones detalladas línea por línea de vida, incluyendo firmas de métodos, tipos de retorno, fragmentos combinados (`alt`, `loop`, `opt`) y llamadas síncronas/asíncronas precisas.

**¿Cuándo usar cada una?**
- Se usa la **Vista Dinámica C4** para comunicar la arquitectura general y la secuencia de comunicación entre módulos/servicios a líderes técnicos, integradores o desarrolladores durante revisiones de diseño.
- Se usa el **Diagrama de Secuencia UML** para guiar la implementación detallada de software, especificando exactamente qué métodos invocar y cómo manejar excepciones en el código.

---

## 5. ¿Qué ventaja concreta tiene modelar con Structurizr DSL frente a dibujar cada vista con C4-PlantUML o Mermaid?

La ventaja principal es que Structurizr DSL es un enfoque de **Modelado de Arquitectura como Código (Single Source of Truth)**, mientras que C4-PlantUML y Mermaid son herramientas de **diagramación independiente**.

**Ventaja Concreta:** En Structurizr DSL se define cada elemento (persona, contenedor, relación) **una sola vez** en la sección `model {}`. Al cambiar el nombre de una tecnología (por ejemplo, cambiar la base de datos a `PostgreSQL 16`), **todas las vistas (Contexto, Contenedores, Despliegue) se actualizan automáticamente** al re-exportar. En C4-PlantUML o Mermaid habría que buscar y modificar manualmente cada archivo de diagrama.

---

## 6. ¿Qué elementos del modelo C4 de su caso se justifican con el ADR-001 del Laboratorio 04? Cite al menos dos.

1. **Contenedor `API Backend` (Monolito Modular):** En la vista de contenedores (Nivel 2) se modeló un único contenedor de aplicación desplegado en Python/Django REST. Esto se justifica directamente en el `ADR-001`, que rechazó la arquitectura de microservicios para garantizar la entrega en 1 mes (`R-01`) y reducir la complejidad operativa.

2. **Contenedores `Worker de Tareas` (Celery) y `Cola y Caché` (Redis):** La separación del procesamiento de notificaciones por WhatsApp en un *worker* asíncrono se justifica en el `ADR-001` y el escenario `QA-02`, garantizando que la caída del servicio externo de mensajería no bloquee ni pierda la persistencia de los pedidos.

---

## 7. Describa un error de la IA al generar o revisar su modelo C4 y cómo lo detectó con la lista de revisión.

Al solicitar el borrador del modelo Structurizr DSL con el Prompt 1, la IA incluyó un nodo llamado `Broker Apache Kafka` dentro del sistema para gestionar los mensajes de WhatsApp.

**Cómo se detectó:** Al aplicar la **Lista de Revisión Oficial de C4** (categoría *Elementos* e *Integridad del Sistema*) y cruzar el borrador contra los `ADRs` del Lab 04, se identificó que Kafka violaba la restricción de presupuesto de infraestructura (`R-03`) y excedía el tiempo de implementación de 1 mes (`R-01`). Se corrigió reemplazándolo por el esquema liviano `Redis + Celery Worker`.

---

## 8. ¿Cómo adaptaría la explicación de su arquitectura para un docente evaluador, un inversionista y un nuevo developer del equipo?

- **Docente Evaluador (Enfoque Técnico y Normativo):** Se explica mediante los **Niveles 2 y 3 (Contenedores y Componentes)**, justificando la trazabilidad entre los *drivers* de calidad (`QA-01` a `QA-05`), las decisiones documentadas en los `ADRs`, la ausencia de ciclos entre módulos y la coherencia del modelo único en Structurizr DSL.

- **Inversionista / Directiva del Mercado (Enfoque de Negocio y Valor):** Se explica únicamente con el **Nivel 1 (Contexto del Sistema)** y la versión no técnica en $\le 120$ palabras: cómo San Camilo en Línea conecta a clientes y comerciantes tradicionalmente no digitalizados, la facilidad de pago con Yape y la continuidad del servicio sin requerir infraestructura costosa.

- **Nuevo Developer del Equipo (Enfoque de Implementación):** Se le presenta la secuencia iniciando en el **Nivel 2 (Contenedores)** para entender la pila tecnológica (React, Django REST, PostgreSQL, Redis), seguido del **Nivel 3 (Componentes)** y el **Diagrama de Clases UML (Nivel 4)** para indicarle la estructura exacta de paquetes/módulos y dónde debe programar una nueva historia de usuario.

