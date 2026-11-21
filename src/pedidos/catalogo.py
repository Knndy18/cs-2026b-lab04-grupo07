"""Módulo de catálogo y visibilidad de productos (San Camilo en Línea)."""

from dataclasses import dataclass
from typing import List


@dataclass
class ProductoCatalogo:
    id_producto: str
    nombre: str
    puesto_id: str
    precio: float
    stock_disponible: int
    activo: bool = True


def obtener_catalogo_visible(productos: List[ProductoCatalogo]) -> List[ProductoCatalogo]:
    """Retorna los productos que deben ser visibles para los clientes en la PWA.
    
    Regla de negocio esperada:
    - Deben estar activos (activo == True)
    - Deben tener stock disponible mayor a cero (stock_disponible > 0)
    """
    # Regla de negocio oficial (Issue #02): visible si está activo y tiene stock estrictamente positivo
    return [
        p for p in productos
        if p.activo and (p.stock_disponible is not None and p.stock_disponible > 0)
    ]
