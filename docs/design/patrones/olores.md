# Reporte de Olores de Código – San Camilo en Línea (`E1`)

## Análisis de Complejidad Ciclomática Inicial (`radon`)

Resultado del análisis sobre `src/pedidos/antes/servicio.py`:
- `ServicioPedidos.procesar_pedido_multipuesto`: **Complejidad Ciclomática = 14 (Clasificación C)**.

---

## Tabla de Olores Detectados y Propuesta de Refactorización

| # | Olor Detectado | Ubicación | Patrón GoF Propuesto | Principio SOLID | Decisión del Equipo |
|---|---|---|---|---|---|
| 1 | `if/elif` por medio de pago que exige modificar el servicio al añadir nuevos métodos. | `servicio.py:59-78` | **Strategy + Adapter + Factory** | **O** (Open/Closed), **D** (Dependency Inversion) | **Aceptado:** Aislará cada pasarela detrás de una interfaz común (`PasarelaPago`). |
| 2 | `if/elif` anidados para calcular la tarifa de delivery según distrito y cantidad de puestos. | `servicio.py:44-53` | **Strategy** | **O** (Open/Closed) | **Aceptado:** Se crearán estrategias de cálculo de delivery intercambiables. |
| 3 | Lógica repetida de reintentos por `TimeoutError` duplicada en cada medio de pago. | `servicio.py:60-76` | **Decorator** | **S** (Single Responsibility) | **Aceptado:** Envolverá las pasarelas para manejar reintentos de forma transparente. |
| 4 | Múltiples condicionales verificando y cambiando manualmente `pedido.estado`. | `servicio.py:32-38` | **State** | **S** (Single Responsibility) | **Aceptado:** Modela el ciclo de vida según la máquina de estados del Lab 05. |
| 5 | Creación manual de cadenas de notificación para WhatsApp y Reportes acopladas al servicio. | `servicio.py:82-84` | **Observer** | **S** (Single Responsibility) | **Aceptado:** Desacoplará las notificaciones permitiendo nuevos suscriptores. |
| 6 | *Propuesta de IA:* Convertir `FabricaPasarelas` en un `Singleton` global. | N/A | **Singleton** | **D** (Dependency Inversion) | **Rechazado:** Introduce estado global y dificulta la inyección de dobles de prueba/Mocks en `pytest`. |
| 7 | *Propuesta de IA:* Usar `Abstract Factory` para crear familias de pagos por ciudad. | N/A | **Abstract Factory** | N/A | **Rechazado (Patternitis):** No existen familias de objetos relacionadas; agregaría sobreingeniería innecesaria. |
