# Issue #03: Error de redondeo en céntimos en liquidación semanal a puesteros

**Reportado por:** Contabilidad del Mercado San Camilo
**Módulo afectado:** `src/pedidos/liquidacion.py`

**Observado:**
Durante la liquidación semanal de ventas hacia los puestos asociados, el cálculo de las retenciones administrativas y el importe neto a transferir acumula discrepancias de céntimos debido al uso de operaciones en coma flotante estándar de Python (`float`). 
Para ventas con precios con céntimos fraccionarios (p. ej. S/ 19.99, S/ 15.55, S/ 12.35) y una retención del 3.5%, el neto resultante no cuadra con el total bruto debido a la precisión finita IEEE 754 (`neto + retencion != total_bruto`), generando saldos pendientes de 1 céntimo que impiden el cierre contable semanal.

**Esperado:**
El cálculo de liquidación semanal debe garantizar que la suma de los importes redondeados a dos decimales de cada partida cumpla estrictamente la ecuación contable:
`round(neto, 2) + round(retencion, 2) == round(total_bruto, 2)`.

**Prueba que reproduce el error:**
`tests/test_issue_03_redondeo.py::test_liquidacion_semanal_redondeo_exacto_centimos`
