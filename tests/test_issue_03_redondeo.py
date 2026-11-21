"""Prueba que reproduce el Issue #03: error de redondeo en céntimos en liquidación semanal."""

import pytest
from src.pedidos.liquidacion import liquidar_puesto


def test_liquidacion_semanal_redondeo_exacto_centimos():
    """La liquidación debe cuadrar al céntimo exacto: neto + retención == total_bruto."""
    ventas = [11.00]  # Con retencion_pct=0.035: 11.00 * 0.035 = 0.385 -> 0.39; neto independiente -> 10.62; suma 11.01
    resultado = liquidar_puesto(ventas, retencion_pct=0.035)

    bruto = resultado["total_bruto"]
    retencion = resultado["retencion"]
    neto = resultado["total_neto"]

    # Validación de la invariante contable:
    assert round(neto + retencion, 2) == round(bruto, 2), (
        f"Descuadre en céntimos: neto ({neto}) + retención ({retencion}) = "
        f"{round(neto + retencion, 2)} != total_bruto ({bruto})"
    )
