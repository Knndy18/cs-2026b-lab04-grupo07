"""Módulo de liquidación financiera a comerciantes (San Camilo en Línea)."""

from typing import Dict, List


def liquidar_puesto(ventas_diarias: List[float], retencion_pct: float = 0.035) -> Dict[str, float]:
    """Calcula la liquidación para un puesto comercial del Mercado San Camilo.
    
    Regla de negocio:
    - total_bruto: suma de ventas del puesto
    - retencion: retención administrativa de la cooperativa (redondeada a 2 decimales)
    - total_neto: importe a transferir al comerciante (debe cuadrar exactamente al céntimo)
    - Invariante contable obligatoria: total_neto + retencion == total_bruto
    """
    total_bruto = round(sum(ventas_diarias), 2)

    # BUG (Issue #03): Calcula retención y neto de manera independiente con round() sobre float,
    # provocando descuadre de 1 céntimo (p. ej. en 11.00: retencion=0.39, neto=10.62 -> suma 11.01 != 11.00)
    retencion = round(total_bruto * retencion_pct, 2)
    total_neto = round(total_bruto - (total_bruto * retencion_pct), 2)

    return {
        "total_bruto": total_bruto,
        "retencion": retencion,
        "total_neto": total_neto
    }
