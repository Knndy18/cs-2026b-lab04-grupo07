# Respuestas al Cuestionario – Caso: San Camilo en Línea

---

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
