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
    # BUG (Issue #02): Solo filtra por activo, permitiendo que productos agotados (stock == 0) sigan visibles
    return [p for p in productos if p.activo]
