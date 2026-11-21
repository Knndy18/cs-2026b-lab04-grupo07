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

    # Corrección: El total neto se obtiene deduciendo directamente la retención redondeada
    retencion = round(total_bruto * retencion_pct, 2)
    total_neto = round(total_bruto - retencion, 2)

    return {
        "total_bruto": total_bruto,
        "retencion": retencion,
        "total_neto": total_neto
    }
