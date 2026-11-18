# Reporte de Métricas y Análisis de Trade-off – San Camilo en Línea (`E6`)

## 1. Tabla Comparativa de Complejidad Ciclomática (`radon cc`) y SLOC

El análisis estático de complejidad ciclomática de McCabe (1976) y de líneas lógicas de código fuente (SLOC) ejecutado con `radon` arrojó las siguientes métricas comparativas entre la versión inicial monolítica (`antes/servicio.py`) y la versión refactorizada con patrones GoF (`despues/servicio.py`, `pagos.py`, `estados.py` y `eventos.py`):

| Métrica / Elemento | Versión Antes (Monolítica) | Versión Después (Patrones) | Impacto / Delta | Justificación de Ingeniería |
|---|---|---|---|---|
| **Complejidad del método principal** | **14 (Clasificación C)** (`procesar_pedido_multipuesto`) | **2 (Clasificación A)** (`procesar_pedido_multipuesto`) | **-85.7%** (Reducción drástica) | Delegación de responsabilidades a clases de estrategia y máquina de estados. |
| **Complejidad ciclomática promedio** | **8.5 (Clasificación B)** | **1.8 (Clasificación A)** | **-78.8%** (Mayor facilidad de testing) | Eliminación total de bloques `if/elif/else` anidados. |
| **Líneas de Código Lógicas (SLOC)** | 88 líneas (`servicio.py`) | 142 líneas (`servicio.py` + `pagos.py`) | +61.3% (Incremento por abstracciones) | Costo deliberado de introducir interfaces (`Protocol`), adaptadores y clases concretas. |
| **Archivos de Código Fuente** | 1 archivo | 2 archivos (`servicio.py`, `pagos.py`) | +1 archivo | Alta cohesión y principio de responsabilidad única (SRP). |
| **Modificación para nuevo medio de pago** | Modificar 1 método central con riesgo de regresión | 0 modificaciones en el código central (extensión pura) | **Cumplimiento total del Principio Open/Closed (OCP)** | Basta con registrar el nuevo adaptador en la fábrica (`FabricaPasarelas.registrar`). |

---

## 2. Análisis del Trade-off (Análisis Honesto)

El refactor hacia los patrones **Strategy, Adapter, Factory, State y Observer** redujo la complejidad ciclomática del método principal de **14 (C)** a **2 (A)**, eliminando las ramificaciones condicionales `if/elif` y delegando la creación y cobro a clases especializadas (Gamma et al., 1994; Fowler, 2018).

### Lo que se ganó (Beneficios Arquitectónicos):
* **Modificabilidad y Extensibilidad Inmediata (OCP):** Para agregar un nuevo medio de pago (como Yape con QR dinámico, Plin v2 o tarjeta de débito), ya no es necesario tocar ni arriesgar la lógica central del `ServicioPedidos` (Martin, 2017).
* **Robustez y Manejo de Fallos:** La fábrica valida el medio de pago antes de alterar el estado del pedido, corrigiendo un fallo crítico de inconsistencia detectado por las pruebas de caracterización.
* **Testabilidad Aislada:** Cada estrategia y adaptador se puede probar de forma 100% aislada utilizando fixtures y dobles de prueba (`pytest`) sin necesidad de levantar el ciclo completo del servicio.

### Lo que costó (Sobrecosto y Penalizaciones):
* **Mayor Volumen de Código (SLOC):** El código pasó de 88 a 142 líneas lógicas (+61.3%). Para un desarrollador novato, leer múltiples clases (`PasarelaPago`, `YapeAdapter`, `FabricaPasarelas`, `EstrategiaPago`) requiere mayor salto cognitivo que leer un script procedural único.
* **Ligera Indirección en Tiempo de Ejecución:** La resolución de clases en tiempo de ejecución agrega una sobrecarga despreciable de microsegundos en Python, ampliamente compensada por la confiabilidad del sistema.

### ¿Cuándo la versión "antes" habría sido suficiente?
Si el sistema *San Camilo en Línea* fuera a operar permanentemente con un único medio de pago (solo Yape manual), sin planes de expansión a otros mercados, sin requerimientos de reintentos asíncronos ni integraciones de modelos de lenguaje (LLM), la versión inicial monolítica habría sido suficiente (Kerievsky, 2004). Los patrones de diseño introducen complejidad estructural que solo se paga por la variabilidad, el crecimiento y la evolución prevista del sistema.

---

## 3. Patrones Rechazados y Justificación Anti-Patternitis

Siguiendo las advertencias contra la *patternitis* (el impulso de forzar patrones donde no se justifican por un olor real), el equipo analizó y descartó explícitamente las siguientes propuestas:

1. **Singleton (para `FabricaPasarelas`):**
   * **Propuesta inicial de la IA:** Instanciar la fábrica como una variable global singleton.
   * **Razón del rechazo:** El patrón Singleton introduce estado global mutable, dificultando la paralelización de pruebas unitarias con `pytest` y acoplando los componentes a una instancia estática (Freeman & Robson, 2020). Se optó por una fábrica parametrizable con inyección de dependencias.
2. **Abstract Factory:**
   * **Propuesta inicial de la IA:** Crear una jerarquía de familias de fábricas de pago para banca móvil vs billeteras.
   * **Razón del rechazo:** No existen familias interdependientes de objetos de pago en el dominio actual. Aplicar `Abstract Factory` habría triplicado la jerarquía de interfaces sin resolver ningún olor real en el código.

---

## 4. Referencias Bibliográficas

* Fowler, M. (2018). *Refactoring: Improving the design of existing code* (2nd ed.). Addison-Wesley.
* Freeman, E., & Robson, E. (2020). *Head first design patterns* (2nd ed.). O'Reilly Media.
* Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design patterns: Elements of reusable object-oriented software*. Addison-Wesley.
* Kerievsky, J. (2004). *Refactoring to patterns*. Addison-Wesley.
* Martin, R. C. (2017). *Clean architecture: A craftsman's guide to software structure and design*. Prentice Hall.
* McCabe, T. J. (1976). *A complexity measure*. IEEE Transactions on Software Engineering, SE-2(4), 308–320.
