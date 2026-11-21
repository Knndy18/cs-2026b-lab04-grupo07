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


---

# Laboratorio 07: Patrones de Diseño y Refactorización

---

## 1. ¿Qué diferencia hay entre un patrón arquitectónico (Laboratorio 04) y un patrón de diseño? Dé un ejemplo de cada uno en su caso.

* **Patrón Arquitectónico (Nivel Macro):** Define la estructura fundamental de alto nivel de todo el sistema, estableciendo subsistemas, contenedores, esquemas de persistencia y responsabilidades de infraestructura. Afecta transversalmente a la aplicación, determina cómo se despliega el software y es sumamente costoso de cambiar una vez implementado.
  * **Ejemplo en San Camilo en Línea:** El patrón **Monolito Modular** (`ADR-001`), que organiza el backend en módulos lógicos cohesivos dentro de un único proceso ejecutable desplegado en un servidor VPS único (`R-03`).

* **Patrón de Diseño (Nivel Micro / Código):** Resuelve problemas recurrentes y localizados de diseño orientado a objetos dentro de un módulo o componente específico. Organiza clases, interfaces y algoritmos para facilitar la modificabilidad y el desacoplamiento sin alterar la arquitectura global.
  * **Ejemplo en San Camilo en Línea:** Los patrones **Strategy y Adapter** (`src/pedidos/pagos.py`), que unifican las APIs dispares de Yape y Plin bajo la abstracción `PasarelaPago`, permitiendo añadir nuevos medios de cobro sin modificar la lógica del servicio de pedidos.

---

## 2. Explique con su código cómo Strategy materializa el principio abierto/cerrado. ¿Qué tuvo que modificar para agregar una variante nueva?

El principio Abierto/Cerrado (*Open/Closed Principle - OCP*) establece que las entidades de software deben estar abiertas para su extensión, pero cerradas para su modificación.

En `src/pedidos/pagos.py`, el patrón **Strategy** materializa OCP a través del protocolo abstracto:

```python
class PasarelaPago(Protocol):
    def cobrar(self, monto: Decimal, referencia: str) -> ComprobantePago:
        ...
```

El orquestador de pedidos (`ServicioPedidos.procesar_pedido_multipuesto`) no conoce si el pago se procesa con Yape, Plin o una pasarela bancaria; únicamente invoca el método polimórfico `pasarela.cobrar(monto, referencia)`.

**¿Qué tuvimos que modificar para agregar una variante nueva (ej. `PlinAdapter`)?**
1. **0 modificaciones en el código núcleo:** La clase `ServicioPedidos` no sufrió ninguna alteración en sus métodos ni condicionales.
2. **Extensión pura:** Se creó una nueva clase que implementa el protocolo (`class PlinAdapter(PasarelaPago)`) y se registró dinámicamente en la fábrica mediante:
   ```python
   FabricaPasarelas.registrar("plin", PlinAdapter)
   ```
El sistema incorporó un nuevo medio de pago cumpliendo OCP de manera rigurosa.

---

## 3. ¿En qué se diferencian Adapter y Decorator si ambos "envuelven" un objeto?

Aunque ambos patrones estructurales utilizan el mecanismo de composición (*wrapping*), persiguen propósitos completamente diferentes:

| Criterio | Patrón Adapter (`src/pedidos/pagos.py`) | Patrón Decorator (`src/pedidos/ia.py`) |
|---|---|---|
| **Intención Principal** | **Convertir una interfaz incompatible** en otra que el cliente espera. | **Añadir responsabilidades o comportamientos adicionales** dinámicamente sin modificar la clase base. |
| **Interfaz Expuesta** | Expone una interfaz **diferente** a la del objeto envuelto (adapta interfaces dispares). | Expone **exactamente la misma interfaz** que el objeto envuelto (es transparente para el cliente). |
| **Ejemplo en el Proyecto** | `YapeAdapter` envuelve el cliente externo de Yape (que espera `telefono` y `token_yape`) y lo adapta al método unificado `cobrar(monto, referencia)`. | `LLMConCache` implementa `ProveedorLLM` y envuelve a cualquier `ProveedorLLM`, interceptando la llamada para responder desde memoria si la consulta ya fue procesada. |

---

## 4. ¿Por qué el patrón State es la implementación natural de un diagrama de máquina de estados? ¿Qué ganó frente a usar condicionales?

En un diagrama UML de máquina de estados, el comportamiento de una entidad está determinado por su estado actual, y cada estado define qué eventos acepta y a qué nuevo estado transita.

El patrón **State** (`src/pedidos/estados.py`) es la implementación orientada a objetos natural porque cada estado del diagrama se convierte en una clase polimórfica (`EstadoBorrador`, `EstadoConfirmado`, `EstadoPagado`, `EstadoCancelado`) que hereda de una clase base abstracta `EstadoPedido`. 

**¿Qué se ganó frente al uso de condicionales?**
1. **Eliminación de la complejidad ciclomática:** Se eliminaron las sentencias anidadas `if estado == 'BORRADOR': ... elif estado == 'PAGADO': ...`, reduciendo la complejidad del ciclo de vida de CC=14 a CC=2.
2. **Prevención de transiciones inválidas:** Intentar pagar un pedido cancelado o cancelar un pedido entregado es rechazado inmediatamente por el propio objeto de estado lanzando la excepción tipada `TransicionInvalidaError`.
3. **Principio de Responsabilidad Única (SRP):** Las reglas de cada estado están encapsuladas en su propia clase, haciendo trivial añadir un nuevo estado (ej. `EstadoEnRuta`) sin riesgo de romper los estados existentes.

---

## 5. ¿Por qué son indispensables las pruebas de caracterización antes de refactorizar? Describa un error que sus pruebas detectaron.

Las **pruebas de caracterización** (Fowler, 2018) son indispensables porque capturan y "congelan" el comportamiento observable actual del código legado antes de realizar cualquier cambio estructural. Sin ellas, una refactorización es un salto al vacío donde es imposible saber si un cambio de diseño alteró inadvertidamente una regla de negocio o introdujo una regresión.

**Error detectado en nuestro caso:**
Al ejecutar las pruebas de caracterización sobre la versión monolítica (`antes/servicio.py`), se detectó un fallo crítico de inconsistencia transaccional: cuando un cliente enviaba un medio de pago no registrado o inválido, la función ejecutaba la confirmación en memoria de los ítems del pedido **antes** de validar la pasarela de pagos. Al fallar el pago, el pedido quedaba en un estado híbrido "confirmado pero sin pago registrado". 
Gracias a las pruebas de caracterización, la refactorización con `FabricaPasarelas` corrigió este defecto validando la existencia de la pasarela y la completitud de la referencia antes de aplicar cualquier mutación de estado.

---

## 6. ¿Qué patrón propuso la IA que ustedes rechazaron y por qué? ¿Qué es la "patternitis"?

Durante la fase de diseño asistido por IA (Interacción 6 de la bitácora de Lab 07), la IA propuso aplicar:
1. **Singleton para `FabricaPasarelas`:** Argumentó que debía existir una única instancia global de la fábrica.
2. **Abstract Factory para la creación de pasarelas:** Sugirió una familia de fábricas dividida entre billeteras móviles y pasarelas bancarias.

**Justificación del Rechazo por el Equipo:**
* **Rechazo de Singleton:** El patrón Singleton introduce estado global mutable, lo cual acopla los tests en `pytest`, dificulta la inyección de pasarelas simuladas (*mocking*) e impide la ejecución concurrente de pruebas.
* **Rechazo de Abstract Factory:** En el dominio de San Camilo no existen múltiples familias de objetos de pago interdependientes; solo existe la familia de adaptadores `PasarelaPago`.

**Definición de "Patternitis":**
Es el antipatrón de diseño y vicio de sobreingeniería en el cual un desarrollador o una IA intenta forzar patrones de diseño complejos en cada rincón del código sin que exista un olor real o una necesidad de variabilidad que lo justifique. La *patternitis* aumenta innecesariamente el número de clases, la indirección y la carga cognitiva, degradando la mantenibilidad del sistema.

---

## 7. ¿Por qué se debe tratar la salida de un LLM como dato no confiable? Describa los guardrails de su caso y qué protegen.

La salida de un modelo de lenguaje (LLM) debe tratarse como **entrada externa no confiable** (*untrusted input*) porque los modelos generativos son sistemas estocásticos y probabilísticos propensos a **alucinaciones** (generación de datos falsos o inexistentes con apariencia de verdad), respuestas fuera de formato y susceptibilidad a manipulaciones adversarias (*prompt injection* o *jailbreaks*). Si sus salidas se conectan directamente a la lógica de negocio o a la base de datos sin sanitizar, pueden provocar pérdidas económicas o fallos de seguridad.

**Guardrails implementados en `src/pedidos/ia.py` (Chain of Responsibility):**
* **Guardrails de Entrada:**
  1. `GuardrailEntradaNoVacia`: Rechaza consultas vacías o de puros espacios en blanco.
  2. `GuardrailLongitudMaxima`: Limita el texto a un máximo de 500 caracteres, mitigando ataques de denegación de servicio por consumo excesivo de tokens.
  3. `GuardrailAntiInyeccion`: Escanea y bloquea patrones típicos de *Prompt Injection* (ej. "ignora instrucciones previas"), inyecciones SQL (`UNION SELECT`, `DROP TABLE`) y secuencias de script maliciosas.
* **Guardrails de Salida:**
  1. `GuardrailFormatoRespuesta`: Valida que la respuesta del LLM cumpla con la estructura requerida por el frontend.
  2. `GuardrailPreciosValidos`: Escanea el texto generado buscando precios en moneda peruana (`S/ X.XX`) y **bloquea inmediatamente cualquier respuesta que ofrezca productos con precio cero (`S/ 0.00`)** o formatos de moneda corrompidos, protegiendo a los comerciantes de San Camilo de ventas fraudulentas por alucinaciones del modelo.

---

## 8. Según sus métricas, ¿valió la pena el refactor? Argumente con la complejidad ciclomática, las líneas de código y los cambios previstos.

**Sí, valió absolutamente la pena.** El análisis cuantitativo con `radon` y el análisis de mantenibilidad sustentan con contundencia esta conclusión:

1. **Reducción Drástica de Complejidad Ciclomática:**
   * El método central de procesamiento de pedidos redujo su complejidad ciclomática de **14 (Clasificación C - Código complejo y riesgoso)** a **2 (Clasificación A - Código simple y lineal)**, lo que representa una **reducción del 85.7%**.
   * La complejidad ciclomática promedio de todo el módulo se redujo en un **78.8%** (de 8.5 a 1.8), permitiendo que la cobertura de pruebas unitarias aumentara de 8 a 58 tests automatizados ejecutados en 0.08 segundos.

2. **Evaluación Honesta de las Líneas de Código (SLOC):**
   * Las líneas de código aumentaron un **+61.3%** (de 88 a 142 SLOC). Sin embargo, este incremento no es código duplicado ni redundante, sino el costo deliberado de introducir contratos explícitos (`Protocol`), manejo tipado de excepciones, clases de estrategia y bucles de reintento ante caídas de red.

3. **Facilidad ante Cambios Previstos:**
   * En la versión monolítica anterior, agregar soporte para un nuevo mercado o un nuevo medio de pago (como Plin o transferencias) requería editar el método central, con un riesgo altísimo de regresión. Con la versión refactorizada, el costo de incorporar un nuevo medio de pago es de **0 líneas modificadas en el código existente**, cumpliendo rigurosamente el Principio Abierto/Cerrado y garantizando la escalabilidad futura de San Camilo en Línea.

---

# Laboratorio 08: Diseño de Arquitectura Guiado por Atributos de Calidad (ADD 3.0, ATAM-lite y Fitness Functions)

---

## 1. ¿En qué se diferencia diseñar la arquitectura con ADD de elegir un estilo arquitectónico como en el Laboratorio 04?

* **Elegir un estilo arquitectónico (Laboratorio 04):** Es una decisión global y estática en la que se selecciona un patrón macro (por ejemplo, Monolito Modular vs. Microservicios) evaluando alternativas generales contra restricciones gruesas de costo y tiempo en una matriz de decisión. Es un punto de partida fundamental pero de grano grueso.

* **Diseñar la arquitectura con ADD 3.0 (Attribute-Driven Design - Laboratorio 08):** Es un **proceso sistemático, iterativo y formal** (Cervantes & Kazman, 2016) guiado paso a paso por los escenarios medibles de mayor prioridad del Árbol de Utilidad. En cada iteración:
  1. Se elige un elemento del sistema a refinar.
  2. Se seleccionan **tácticas arquitectónicas específicas** (no solo estilos) para controlar las medidas de respuesta de los atributos de calidad dominantes.
  3. Se generan y evalúan conceptos de diseño descartando opciones no viables.
  4. Se respalda cada decisión con **evidencia cuantitativa** (simulaciones matemáticas de colas M/M/c, modelos Monte Carlo o prototipos).
  5. Se documentan las decisiones en ADRs y se actualiza la trazabilidad en C4.

---

## 2. ¿Para qué sirve calificar los escenarios con (importancia, dificultad)? ¿Qué escenario de su árbol tiene la mayor prioridad y por qué?

* **Propósito de la calificación (Importancia, Dificultad) en {H, M, L} x {H, M, L}:**
  Permite construir la matriz de priorización del Árbol de Utilidad. Aquellos escenarios calificados como **(H, H)** (Alta Importancia para los objetivos de negocio y Alta Dificultad técnica de implementación) representan el mayor riesgo arquitectónico y deben ser abordados de forma obligatoria en las primeras iteraciones de ADD. Los escenarios (L, L) se difieren o no requieren diseño arquitectónico dedicado.

* **Escenario con Mayor Prioridad en San Camilo en Línea 2.0:**
  Los escenarios dominantes son:
  * **QA-01 (Modificabilidad - Expansión Multitenant):** Incorporar los mercados Altiplano y Río Seco en <= 1 día sin modificar el código fuente del núcleo. Calificación: **(H, H)**.
  * **QA-03 (Disponibilidad - Resiliencia en Pagos):** Ante una caída de 20 minutos de las pasarelas externas Yape/Plin, el sistema debe registrar **0 pedidos perdidos** mediante el patrón transaccional Outbox y reintentos asíncronos. Calificación: **(H, H)**.

  **¿Por qué tienen la mayor prioridad?** Porque perder un pedido confirmado destruye la confianza económica de los comerciantes y clientes (`R-06`), y la viabilidad del negocio depende críticamente de expandirse rápidamente a los mercados Altiplano y Río Seco bajo una arquitectura multitenant antes de que culmine el mes de plazo (`R-01`).

---

## 3. ¿Qué diferencia hay entre una táctica y un patrón? Ilustre con el circuit breaker.

* **Táctica Arquitectónica:** Es una decisión de diseño fundamental, atómica y focalizada que influye directamente en el control de la respuesta de un único atributo de calidad. No prescribe código ni diagramas; es el principio operativo subyacente (Bass et al., 2021). Ejemplos: *"Falla Rápida" (Fail Fast)*, *"Encolar Solicitudes"*, *"Caché de Respuestas"*.

* **Patrón Arquitectónico / de Diseño:** Es un paquete estructurado y reutilizable de decisiones de diseño que define componentes, clases, estados y secuencias de interacción para materializar una o varias tácticas de manera concreta en software.

* **Ilustración con el Circuit Breaker:**
  * **Tácticas que implementa:**
    1. *Prevenir fallas en cascada:* Evita que los hilos del servidor web se queden bloqueados esperando a un servicio externo caído.
    2. *Falla Rápida:* Responde de inmediato con error controlado sin saturar la red.
    3. *Monitoreo y recuperación gradual:* Evalúa periódicamente si el servicio remoto se restableció.
  * **El Patrón:** Define la máquina de estados con tres estados concretos (`Closed`, `Open`, `Half-Open`), contadores de fallos, temporizadores de enfriamiento (*reset timeout*) y contratos de fallback para aislar las llamadas hacia las APIs de Yape y Plin.

---

## 4. Describa un punto de sensibilidad y un punto de trade-off de su arquitectura, con la evidencia que los respalda.

* **Punto de Sensibilidad (`S1` - Rendimiento y Tasa de Aciertos de Caché):**
  * *Definición:* El tiempo de respuesta percentil 95 ($p95 \le 1.5\text{ s}$) del catálogo ante ráfagas concurrentes de $20\text{ req/s}$ depende fuertemente de que la tasa de aciertos (*Hit Rate*) de la caché en Redis no descienda del **$15\%$**.
  * *Evidencia Cuantitativa:* La simulación matemática de teoría de colas $M/M/c$ (`fitness/rendimiento.py`) demuestra que con una tasa de aciertos de caché del **$60\%$**, el tiempo de respuesta promedio es de $27.4\text{ ms}$ y el $p95$ es de **$72.4\text{ ms}$**. Si la caché se desactiva (Hit Rate $= 0\%$), el $100\%$ de las peticiones golpea la base de datos PostgreSQL, incrementando la utilización de los workers al $82\%$ y elevando el $p95$ a $>1.8\text{ s}$, violando el presupuesto de latencia.

* **Punto de Trade-off (`T1` - Rendimiento vs. Frescura de Datos):**
  * *Definición:* La adopción de la táctica de caché en Redis para el catálogo general con un tiempo de expiración (TTL) de 30 segundos mejora drásticamente el rendimiento, pero introduce una inconsistencia temporal en la visualización de stock para los clientes.
  * *Evidencia Cuantitativa:* Acelera la respuesta en un **$95\%$** y reduce la carga en disco, pero durante picos de compra simultánea de un mismo producto en los mercados San Camilo y Río Seco, un cliente podría visualizar disponible un producto que se agotó hace 10 segundos, obligando a realizar una validación transaccional secundaria en base de datos al momento de confirmar el carrito (`RF-02`, `RF-03`).

---

## 5. ¿Qué supuestos hizo su simulación y cómo podrían invalidar la decisión si fueran falsos?

En la simulación matemática de rendimiento basada en colas $M/M/c$ con modelo Erlang C (`fitness/rendimiento.py`), se asumieron los siguientes supuestos:

1. **Llegadas según un proceso de Poisson homogéneo:** Se asume que las solicitudes de los usuarios llegan de forma independiente con una tasa media constante de $\lambda = 20\text{ peticiones/segundo}$.
2. **Tiempos de servicio con distribución exponencial:** Se asume que los tiempos de consulta en Redis ($2\text{ ms}$) y PostgreSQL ($45\text{ ms}$) siguen distribuciones exponenciales de memoria nula.
3. **Distribución homogénea de aciertos de caché (Ley de Pareto / 80-20):** Se asume que las consultas se concentran en el catálogo popular alcanzando un $60\%$ de aciertos.

**¿Cómo se invalidaría la decisión si fueran falsos?**
* Si en la vida real el tráfico ocurre en **ráfagas aperiódicas masivas (*micro-bursts*)** donde llegan 100 peticiones en menos de 200 ms (tráfico auto-similar o fractal), la cola superará la capacidad de los $c=4$ workers de Gunicorn, provocando rechazos de conexión HTTP 504.
* Si el patrón de consulta de los usuarios es de **cola larga (*long-tail*)**, donde cada cliente consulta productos exóticos distintos nunca antes cacheados, el Hit Rate colapsará hacia el $0\%$, saturando la CPU del único servidor VPS (`R-03`) y obligando a redimensionar la memoria RAM o añadir réplicas de lectura de PostgreSQL.

---

## 6. ¿Qué riesgo de la evaluación cruzada aceptaron sin mitigarlo y por qué es razonable para un plazo de 1 mes?

* **Riesgo Aceptado sin Mitigación (`R2` - Servidor VPS Único como Punto Único de Falla / SPOF):**
  Durante la evaluación cruzada ATAM-lite con el Grupo 06, el evaluador adversario señaló como riesgo crítico que toda la plataforma backend (API Django, Celery Worker, Redis y PostgreSQL) se ejecuta en un único servidor VPS en la nube (`R-03`). Si la instancia física del proveedor sufre un apagón o fallo de hardware, los tres mercados (San Camilo, Altiplano y Río Seco) quedan inoperativos simultáneamente.

* **Por qué es plenamente razonable para un plazo de 1 mes (`R-01`):**
  Diseñar e implementar una infraestructura de Alta Disponibilidad (HA) multi-región con balanceadores de carga redundantes, clústeres de base de datos distribuidos con replicación sincrónica y failover automatizado triplicaría el presupuesto del proyecto (violando `R-03`) y consumiría semanas enteras de esfuerzo de DevOps para un equipo de 3 desarrolladores (`R-02`), impidiendo entregar el software funcional a tiempo.
  El riesgo se asumió de forma consciente y pragmática, mitigándolo con una salvaguarda operativa liviana: **copias de seguridad automatizadas diarias de PostgreSQL enviadas a almacenamiento en frío externo (S3/Cloud Storage)**, garantizando un RPO <= 24 horas sin sobrecostos de operación.

---

## 7. Explique qué es una fitness function y qué degradación concreta de su arquitectura detectaría cada una de las suyas.

Una **Fitness Function Arquitectónica** (Ford, Parsons, Kua y Sadalage, 2022) es una prueba o métrica objetiva, automatizada y ejecutable dentro del pipeline de Integración Continua (CI) que evalúa y protege la integridad de una característica o atributo arquitectónico frente a la degradación silenciosa del software con el paso del tiempo.

**Degradaciones concretas que detectan las nuestras:**
1. **`fitness/rendimiento.py` (Fitness Function de Rendimiento):**
   * *Degradación que detecta:* Detecta si una modificación en los modelos de Django introduce consultas N+1 en la base de datos que eleven el tiempo de servicio o si se reduce el número de workers, provocando que el tiempo de respuesta percentil 95 supere el presupuesto contractual de **$p95 > 1.5\text{ segundos}$** ante $20\text{ req/s}$.
2. **`fitness/disponibilidad.py` (Fitness Function de Disponibilidad y Resiliencia):**
   * *Degradación que detecta:* Mediante simulación Monte Carlo de 1,000 iteraciones con caídas simuladas de Yape/Plin, detecta si un cambio en el tamaño de la cola o en la política de reintentos provoca que se pierda un solo pedido (**$\text{pedidos\_perdidos} > 0$**), rompiendo la garantía del patrón Outbox (`QA-03`).
3. **Fitness Function Estructural (`.importlinter` / `import-linter`):**
   * *Degradación que detecta:* Detecta importaciones prohibidas y dependencias circulares entre los módulos del Monolito Modular (ej. si un desarrollador introduce accidentalmente `from pedidos import ...` dentro del módulo `catalogo` o `notificaciones`), rompiendo la arquitectura en capas y bloqueando el despliegue en GitHub Actions.
4. **Fitness Function de Seguridad Multitenant (Test Automatizado de RLS):**
   * *Degradación que detecta:* Detecta si una nueva tabla de productos o pedidos omitió la directiva `ENABLE ROW LEVEL SECURITY` en PostgreSQL, ejecutando una consulta automatizada en CI con el token del Mercado Altiplano y verificando que devuelva estrictamente **0 filas** del Mercado San Camilo (`QA-02`).

---

## 8. ¿Qué propuesta de la IA rechazaron con evidencia? ¿Qué habría pasado si la aceptaban sin medir?

* **Propuesta de la IA:**
  Durante la Iteración 1 de ADD (Interacción 2 de la bitácora de Lab 08), el asistente de IA afirmó que para soportar la expansión concurrente de los tres mercados (San Camilo, Altiplano y Río Seco), la arquitectura de Monolito Modular del Lab 04 colapsaría, y recomendó migrar de inmediato a una arquitectura de **Microservicios orquestada en clúster Kubernetes (EKS)** con bases de datos independientes por mercado.

* **Evidencia Cuantitativa con la que se rechazó:**
  El equipo ejecutó el script de simulación matemática $M/M/c$ (`fitness/rendimiento.py`) modelando la carga total agregada de los tres mercados en hora pico ($20\text{ req/s}$). La simulación demostró con datos matemáticos rigurosos que:
  * El Monolito Modular con 4 workers atiende el tráfico con una **utilización de CPU de apenas el 35%** en el VPS actual.
  * Con la caché en Redis activa (Hit Rate = 60%), el tiempo de espera en cola es virtualmente nulo ($W_q = 0.0001\text{ s}$) y el $p95$ es de apenas **$72.4\text{ ms}$**, muy por debajo del límite de $1.5\text{ s}$.

* **¿Qué habría pasado si la aceptaban sin medir?**
  1. **Fracaso en el plazo del proyecto (`R-01`):** El equipo habría consumido semanas configurando clústeres Kubernetes, mallas de servicios (*Service Mesh*), pipelines de CI/CD distribuidos y transacciones distribuidas con patrón Saga.
  2. **Violación presupuestal (`R-03`):** El costo de múltiples nodos en la nube y balanceadores gestionados habría multiplicado por cinco el presupuesto mensual del mercado.
  3. **Colapso por memoria RAM:** Intentar correr clústeres de microservicios sobre el VPS único habría saturado la memoria RAM, desatando el *OOM Killer* de Linux y dejando la plataforma completamente inoperativa.

---

# Laboratorio 10: Sistemas agénticos en la construcción de software

## 1. ¿Qué diferencia a un agente de un flujo de trabajo fijo? Dé un ejemplo de su proyecto en el que un flujo de trabajo sea mejor opción.

### Diferencia Conceptual y Operativa
La distinción fundamental radica en **quién gobierna el flujo de control y la toma de decisiones** durante la ejecución (Anthropic, 2024; Albada, 2025):

* **Flujo de trabajo fijo (*Workflow*):**
  * La secuencia de pasos, bifurcaciones condicionales, reintentos y llamadas a funciones están **estáticamente codificados por el programador** mediante estructuras tradicionales (`if/else`, bucles, canalizaciones DAG).
  * Si se incorpora un modelo de lenguaje (LLM), este opera exclusivamente como un componente de transformación o extracción puntual (por ejemplo, resumir un texto o clasificar una categoría predeterminada) dentro de una caja fija.
  * *Ventajas:* Comportamiento 100% determinista, costo computacional mínimo, latencia baja y predecible, y facilidad absoluta de pruebas unitarias.

* **Agente de IA:**
  * El sistema recibe un **objetivo de alto nivel** (p. ej., "reproducir y corregir el Issue #01 en el código").
  * El modelo de lenguaje actúa como el motor de razonamiento central que **decide de forma autónoma y dinámica qué acciones tomar**, qué herramientas invocar, qué argumentos suministrar y en qué orden ejecutarlas (Grootendorst & Alammar, 2026, cap. 1).
  * Opera en un **bucle cerrado ReAct (Pensamiento $\to$ Acción $\to$ Observación)**: evalúa el resultado retornado por el entorno (la salida de una prueba, el diff de un archivo o un error de ejecución) y reformula su siguiente paso hasta declarar cumplido el objetivo o agotar su presupuesto de pasos.

### Ejemplo en San Camilo en Línea donde un flujo de trabajo fijo es la mejor opción
En la plataforma **San Camilo en Línea**, el **proceso de cobro transaccional y confirmación de pedidos multipuesto** (`ServicioPedidos.procesar_pedido_multipuesto`) es el caso paradigmático donde un flujo de trabajo fijo es rotundamente superior:

```
[Cliente confirma Carrito] 
       ↓
[Validar estado BORRADOR y líneas no vacías]
       ↓
[Calcular subtotal + tarifa delivery por distrito]
       ↓
[Invocar pasarela mediante YapeAdapter (Strategy)]
       ↓
[Si aprobado: estado = PAGADO, registrar outbox, emitir confirmación WhatsApp]
[Si rechazado: estado = CANCELADO]
```

**Justificación técnica:**
1. **Determinismo financiero estricto:** El cálculo de tarifas y la invocación de la API de Yape no admiten creatividad ni ambigüedad probabilística. Un agente autónomo podría alucinar un paso intermedio o alterar el monto a transferir.
2. **Latencia y SLA:** Un flujo fijo se ejecuta en menos de **$150\text{ ms}$**; un agente autónomo intercalando llamadas al LLM demandaría entre 5 y 15 segundos por turno, destruyendo la experiencia de usuario en la PWA (violando `QA-01` y el presupuesto $p95 \le 1.5\text{ s}$).
3. **Costo de infraestructura:** Una función Python compilada cuesta cero llamadas a modelos generativos; delegar un checkout a un agente multiplicaría exponencialmente el consumo de tokens para un equipo con presupuesto reducido (`R-03`).

---

## 2. Elija dos arquetipos de agentes (Sección 1.3) y explique cuál usaría para cada uno de sus tres issues.

### Arquetipos Seleccionados (Albada, 2025, cap. 5; Koenigstein, 2026)
1. **Arquetipo ReAct (*Reasoning + Acting* - Yao et al., 2023):**
   Intercala pasos explícitos de razonamiento verbal y ejecución de herramientas en un bucle adaptativo. Es el patrón óptimo para tareas exploratorias donde la localización de la falla, los efectos colaterales y las observaciones intermedias condicionan dinámicamente los siguientes pasos.
2. **Arquetipo Planificador-Ejecutor (*Plan-and-Solve*):**
   Desacopla el razonamiento en dos fases: primero un agente planificador genera un plan de pasos estructurado y estático; posteriormente, un agente ejecutor sigue el plan de forma secuencial y acotada. Es ideal para tareas con pasos definidos, reduciendo alucinaciones y minimizando el consumo de tokens de contexto.

### Asignación y Justificación para los Tres Issues de San Camilo en Línea

| Issue | Descripción del problema | Arquetipo elegido | Justificación técnica en el contexto del código |
|---|---|---|---|
| **Issue #01** | *Un pedido a varios puestos cobra dos veces la comisión base* (`src/pedidos/comisiones.py`) | **ReAct** | La causa exacta requiere exploración: el agente debe ejecutar las pruebas para observar el fallo inicial (`5.00 != 3.50`), buscar las funciones de cálculo, leer el archivo de comisiones, sortear comentarios engañosos de inyección indirecta (que intentan ejecutar scripts no autorizados con `curl`), editar la fórmula multiplicadora y re-ejecutar las pruebas. La capacidad de observar y reaccionar paso a paso es indispensable. |
| **Issue #02** | *Producto agotado sigue visible en el catálogo de puestos* (`src/pedidos/catalogo.py`) | **Planificador-Ejecutor** | Es un cambio determinista y de bajo riesgo con pasos previsibles: (1) Localizar la función `obtener_catalogo_visible`, (2) Inspeccionar la condición de filtrado por lista, (3) Añadir la condición `and p.stock_disponible > 0`, y (4) Verificar con `pytest tests/test_issue_02_catalogo.py`. Un plan previo de 4 pasos evita que el agente divague o consuma contexto innecesario. |
| **Issue #03** | *Error de redondeo en céntimos en liquidación semanal* (`src/pedidos/liquidacion.py`) | **ReAct (con reflexión contable)** | Los errores de redondeo de punto flotante binario (IEEE 754) en sumas financieras a menudo requieren ajustar estrategias: si se redondea cada partida por separado, la suma no cuadra con el bruto. El bucle ReAct permite al agente formular una hipótesis de corrección (p. ej. derivar el neto como `total_bruto - retencion`), ejecutar la prueba de balance exacto de céntimos, y si la invariante contable falla, reflexionar sobre la discrepancia y ajustar el redondeo hasta obtener verde. |

---

## 3. Describa la máquina de estados de su agente. ¿Qué guardia evita que el agente se ejecute indefinidamente?

### Descripción de la Máquina de Estados del Agente (Koenigstein, 2026, cap. 1)
La máquina de estados finitos del agente ReAct implementada en `agentes/agente/nucleo.py` estructura y confina la ejecución del LLM bajo un protocolo formal con los siguientes estados:

1. **`INICIO`:**
   * Estado inicial al recibir el objetivo del usuario (`historial[0]`). Inicializa el temporizador de alta resolución y el registro de eventos en la traza JSONL.
2. **`DECIDIENDO`:**
   * El LLM recibe la ventana de contexto acumulada (objetivo, historial de herramientas y observaciones previas) y propone una decisión codificada en JSON.
3. **`VALIDANDO_CONTRATO`:**
   * Se comprueba deterministamente que la respuesta del LLM satisfaga el contrato estructurado mediante `validar_decision`: existencia de `pensamiento`, presencia disyuntiva exclusiva de `accion` o `final`, ausencia de campos extra no permitidos y que la herramienta pertenezca al catálogo conocido.
   * *Transición condicional:* Si el contrato se incumple (`[inválida]`), transita a `CONTRATO_INVALIDO` y devuelve un mensaje de error como observación al historial para que el modelo se autocorrija en el estado `DECIDIENDO`. Si contiene `final`, transita a `FINALIZADO`. Si propone `accion`, transita a `EVALUANDO_POLITICA`.
4. **`EVALUANDO_POLITICA`:**
   * Capa de guardrails que filtra la acción propuesta (`Politica.evaluar`): verifica el sandbox de archivos, valida que los comandos CLI pertenezcan a la lista blanca (`pytest`, `radon`, `git`), bloquea ediciones sobre rutas protegidas (`tests/`) y verifica si se superó el presupuesto de pasos.
   * *Transición condicional:* Si se deniega, transita a `BLOQUEADO` y retroalimenta al modelo; si requiere validación humana transita a `ESPERANDO_APROBACION`; si es válida, transita a `EJECUTANDO`.
5. **`ESPERANDO_APROBACION` (Human-in-the-Loop):**
   * El sistema suspende la ejecución y solicita confirmación humana (`s/n`) ante modificaciones críticas de código. Si el humano rechaza, transita a `DECIDIENDO` con la observación de rechazo.
6. **`EJECUTANDO`:**
   * Ejecución determinista de la herramienta real (`Herramientas`) dentro del entorno seguro. Si la herramienta genera una excepción inesperada, esta se captura limpiamente como texto sin romper el agente.
7. **`OBSERVANDO`:**
   * La salida de la herramienta o el mensaje de error se recortan al tamaño máximo permitido y se incorporan al historial conversacional con el rol `user`. El ciclo retorna automáticamente a `DECIDIENDO`.
8. **`FINALIZADO` (Estado Terminal Exitoso):**
   * Se alcanza cuando el modelo emite `"final"` tras haber validado la resolución con las pruebas en verde. Escribe la traza JSONL completa y devuelve la solución.
9. **`LIMITE_ALCANZADO` (Estado Terminal por Presupuesto):**
   * Se alcanza cuando se agota el número de pasos autorizados sin llegar a una respuesta final válida, previniendo bucles infinitos.

### ¿Qué guardia evita que el agente se ejecute indefinidamente?
La guardia explícita que protege al sistema de bucles infinitos es:
$$\mathbf{[\text{paso} \le \text{max\_pasos}]}$$

Implementada a nivel de política y control de bucle:
```python
# agente/politica.py
if paso > self.max_pasos:
    return Decision(False, f"Se alcanzó el máximo de {self.max_pasos} pasos")

# agente/nucleo.py
for paso in range(1, self.politica.max_pasos + 2):
    ...
```

**Mecanismo de protección:**
Si el agente entra en un bucle repetitivo de razonamiento, reitera llamadas erróneas o el asistente sufre una alucinación cíclica, cada ciclo incrementa el contador determinista `paso`. Al intentar ejecutar una acción en el paso $\text{max\_pasos} + 1$ (configurado por defecto en 15 pasos en `Politica`), la guardia evalúa a **Falso**, el método emite un veredicto de bloqueo indicando que se alcanzó el límite, la máquina de estados transita de inmediato a **`LIMITE_ALCANZADO`**, se interrumpe el bucle con `break` y se cierra la sesión persistiendo la traza. Esto garantiza un techo estricto e inviolable sobre el consumo de tokens, el tiempo de CPU y el costo económico de la plataforma.
