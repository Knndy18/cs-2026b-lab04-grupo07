"""Prueba que reproduce el Issue #02: producto agotado sigue visible en el catálogo."""

import pytest
from src.pedidos.catalogo import ProductoCatalogo, obtener_catalogo_visible


def test_producto_agotado_no_aparece_en_catalogo():
    """Productos con stock 0 no deben incluirse en el catálogo visible."""
    p1 = ProductoCatalogo("PRD-01", "Manzana Israel", "P12", 4.50, stock_disponible=10, activo=True)
    p2 = ProductoCatalogo("PRD-02", "Plátano Seda", "P12", 3.00, stock_disponible=0, activo=True)
    p3 = ProductoCatalogo("PRD-03", "Papaya Arequipeña", "P12", 6.00, stock_disponible=5, activo=True)
    p4 = ProductoCatalogo("PRD-04", "Uva Borgoña", "P12", 7.00, stock_disponible=8, activo=False)

    visibles = obtener_catalogo_visible([p1, p2, p3, p4])
    ids_visibles = [p.id_producto for p in visibles]

    # p2 tiene stock 0 y p4 está inactivo -> solo deben estar p1 y p3
    assert ids_visibles == ["PRD-01", "PRD-03"], f"Catálogo visible incluye productos no deseados: {ids_visibles}"
