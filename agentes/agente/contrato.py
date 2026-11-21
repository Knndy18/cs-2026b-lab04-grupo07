"""Validación del contrato estructurado de decisiones del agente (Koenigstein, 2026, cap. 5)."""

from typing import Any, Dict, Set, Tuple


def validar_decision(d: Any, herramientas_conocidas: Set[str]) -> Tuple[bool, str]:
    """Valida que una decisión cumpla estrictamente con el contrato JSON del protocolo.
    
    Reglas del contrato:
    1. Debe ser un diccionario/objeto JSON.
    2. Debe contener la clave 'pensamiento' (texto no vacío).
    3. Debe contener 'accion' o 'final', pero nunca ambos simultáneamente ni ninguno.
    4. No se permiten claves adicionales fuera de {'pensamiento', 'accion', 'args', 'final'}.
    5. Si contiene 'final', su valor debe ser un string.
    6. Si contiene 'accion', debe pertenecer al catálogo de herramientas conocidas.
    7. 'args' es opcional, pero si está presente debe ser un diccionario/objeto JSON.
    """
    if not isinstance(d, dict):
        return False, "la decisión debe ser un objeto JSON"
    if not isinstance(d.get("pensamiento"), str) or not d["pensamiento"].strip():
        return False, "falta 'pensamiento' (texto no vacío)"
    if ("final" in d) == ("accion" in d):
        return False, "debe incluir 'accion' o 'final', pero no ambos"
    
    extra = set(d) - {"pensamiento", "accion", "args", "final"}
    if extra:
        return False, f"campos no permitidos: {sorted(extra)}"

    if "final" in d:
        return (True, "") if isinstance(d["final"], str) else (False, "'final' debe ser texto")
    if d["accion"] not in herramientas_conocidas:
        return False, f"herramienta desconocida: {d['accion']!r}"
    if not isinstance(d.get("args", {}), dict):
        return False, "'args' debe ser un objeto JSON"

    return True, ""
