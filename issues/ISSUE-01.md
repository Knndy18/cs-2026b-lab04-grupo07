# Issue #01: Un pedido a varios puestos cobra dos veces la comisión base

**Reportado por:** Administración y tesorería del Mercado San Camilo
**Módulo afectado:** `src/pedidos/comisiones.py`

**Observado:**
Al procesar un pedido multipuesto que involucra artículos de dos o más puestos independientes (por ejemplo, Puesto 12 "Frutas Doña María" y Puesto 34 "Verduras Don Pedro"), la plataforma duplica la tarifa base administrativa fija. En lugar de cobrar una única tasa base fija de **S/ 1.50** por pedido más el 5% del subtotal, el sistema multiplica los S/ 1.50 por cada puesto único detectado en las líneas del pedido.
Por ejemplo, para un pedido con subtotal de **S/ 40.00** dividido entre 2 puestos:
- La comisión esperada es: `S/ 1.50 (base fija) + S/ 2.00 (5% de 40.00) = S/ 3.50`.
- El sistema cobra: `(2 * S/ 1.50) + S/ 2.00 = S/ 5.00` (sobrecargo erróneo de S/ 1.50).

**Esperado:**
La comisión fija administrativa debe cobrarse **exactamente una sola vez por pedido global**, independientemente de la cantidad de puestos involucrados en el pedido multipuesto, sumada a la tasa variable porcentual (5.0%).

**Prueba que reproduce el error:**
`tests/test_issue_01_comision.py::test_pedido_multipuesto_no_duplica_comision_base`
