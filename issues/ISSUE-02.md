# Issue #02: Producto agotado sigue visible en el catálogo de puestos

**Reportado por:** Comerciantes y clientes del Mercado San Camilo
**Módulo afectado:** `src/pedidos/catalogo.py`

**Observado:**
En la consulta de catálogo por puesto, los productos que se quedan sin existencias (`stock_disponible = 0`) o cuyo estado de inventario es nulo continúan apareciendo en los resultados visibles de la aplicación web. Los clientes agregan estos ítems a su cesta y el pedido falla recién en la fase de despacho o genera rechazos por parte de los puesteros.
La función `obtener_catalogo_visible(productos)` únicamente filtra la condición `p.activo is True`, ignorando la validación del stock restante.

**Esperado:**
La función de consulta de catálogo debe retornar única y exclusivamente aquellos productos que satisfagan ambas condiciones de visibilidad: estar activos (`activo is True`) y contar con stock disponible estrictamente positivo (`stock_disponible > 0`).

**Prueba que reproduce el error:**
`tests/test_issue_02_catalogo.py::test_producto_agotado_no_aparece_en_catalogo`
