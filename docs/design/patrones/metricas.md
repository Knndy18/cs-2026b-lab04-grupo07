# Reporte de Métricas y Análisis de Trade-off – San Camilo en Línea (`E6`)

## 1. Tabla Comparativa de Complejidad Ciclomática (`radon cc`) y SLOC

| Métrica / Elemento | Versión Antes (Monolítica) | Versión Después (Patrones) | Impacto / Delta |
|---|---|---|---|
| **Complejidad del método principal** | **14 (Clasificación C)** (`procesar_pedido_multipuesto`) | **2 (Clasificación A)** (`procesar_pedido_multipuesto`) | **-85.7%** (Reducción drástica) |
| **Complejidad promedio del código** | **8.5 (Clasificación B)** | **1.8 (Clasificación A)** | **-78.8%** (Código mucho más simple de probar) |
| **Líneas de Código de Lógica (SLOC)** | 88 líneas (`servicio.py`) | 142 líneas (`servicio.py` + `pagos.py`) | +61.3% (Incremento por clases e interfaces) |
| **Archivos de Código Fuente** | 1 archivo | 2 archivos (`servicio.py`, `pagos.py`) | +1 archivo |
| **Métodos a modificar para nuevo medio de pago** | 1 método (Modificando `if/elif` en el servicio) | 0 métodos (Extendiendo registrando en la Factory) | **Cumplimiento total del Principio Open/Closed** |

---

## 2. Análisis del Trade-off (Análisis Honesto)

El refactor hacia los patrones **Strategy, Adapter y Factory** redujo la complejidad ciclomática del método principal de **14 (C)** a **2 (A)**, eliminando las ramificaciones condicionales `if/elif` y delegando la creación y cobro a clases especializadas[cite: 25, 29, 30].

* **Lo que se ganó:** Modificabilidad y extensibilidad inmediatas. Para agregar un nuevo medio de pago (como Yape con QR o Plin v2), ya no es necesario tocar ni arriesgar la lógica central del `ServicioPedidos`[cite: 24, 29, 38]. Además, la Factory valida el medio de pago antes de alterar el estado del pedido, corrigiendo un fallo detectado por las pruebas[cite: 35].
* **Lo que costó:** Mayor cantidad de líneas de código (SLOC pasó de 88 a 142) y una ligera indirección al introducir interfaces abstractas y adaptadores[cite: 23, 30, 36].
* **¿Cuándo la versión "antes" habría sido suficiente?** Si el sistema San Camilo en Línea fuera a operar permanentemente con un único medio de pago sin planes de expansión ni requerimientos de reintentos o integraciones de IA, la versión "antes" habría sido suficiente[cite: 36]. Los patrones solo se justifican por la variabilidad y evolución prevista del sistema[cite: 23, 36].

---

## 3. Patrones Rechazados y Justificación

1. **Singleton (para `FabricaPasarelas`):**
   * **Razón del rechazo:** Almacenar la fábrica como una instancia global introduce estado global mutable, dificultando el aislamiento de pruebas unitarias y la inyección de pasarelas simuladas con `pytest`[cite: 23, 29].
2. **Abstract Factory:**
   * **Razón del rechazo (Patternitis):** No existen familias de objetos de pago interdependientes. Usar `Abstract Factory` habría agregado una jerarquía de clases redundante sin resolver ningún olor real[cite: 26, 29].
