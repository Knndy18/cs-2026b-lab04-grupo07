"""Prueba que reproduce el Issue #01: duplicación de comisión en pedido multipuesto."""

import pytest
from src.pedidos.comisiones import ItemComision, calcular_comision_pedido


def test_pedido_multipuesto_no_duplica_comision_base():
    """Un pedido con 2 puestos y S/ 40.00 de subtotal debe cobrar S/ 1.50 fija + S/ 2.00 variable = S/ 3.50."""
    items = [
        ItemComision(puesto_id="PUESTO-12-FRUTAS", subtotal=25.0),
        ItemComision(puesto_id="PUESTO-34-VERDURAS", subtotal=15.0),
    ]

    # Esperado: 1.50 + (40.0 * 0.05) = 1.50 + 2.00 = 3.50
    comision = calcular_comision_pedido(items)
    assert comision == 3.50, f"Se esperaba comisión de S/ 3.50 pero se obtuvo S/ {comision} (comisión duplicada)"
