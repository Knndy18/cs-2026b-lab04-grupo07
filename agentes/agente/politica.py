"""Política de guardrails y control de ejecución por rol (Koenigstein, 2026, cap. 6)."""

import re
from dataclasses import dataclass, field
from typing import Callable, Optional, Set, Tuple


def pedir_aprobacion_humana(args: dict) -> bool:
    """Solicita confirmación por consola mostrando antes/después y repitiendo hasta recibir 's' o 'n'."""
    ruta = args.get("ruta", "(sin ruta)")
    antes = args.get("antes", "")
    despues = args.get("despues", "")
    print("\n[HUMAN-IN-THE-LOOP] Solicitud de edición de código:")
    print(f"Archivo: {ruta}")
    print("--- Fragmento ANTES:")
    print(antes)
    print("--- Fragmento DESPUÉS:")
    print(despues)
    while True:
        resp = input("¿Aprobar edición? (s/n): ").strip().lower()
        if resp == "s":
            return True
        elif resp == "n":
            return False
        print("Entrada inválida. Ingrese exactamente 's' para aprobar o 'n' para rechazar.")


@dataclass
class Decision:
    permitido: bool
    motivo: str = ""


@dataclass
class Politica:
    """Define las restricciones de seguridad que toda acción propuesta debe atravesar."""
    herramientas_permitidas: Set[str] = field(default_factory=lambda: {
        "listar_archivos", "leer_archivo", "buscar", "ejecutar_pruebas",
        "editar_archivo", "ejecutar_comando", "ver_cambios",
        "mapa_repo", "anotar", "leer_notas"
    })
    comandos_permitidos: Tuple[str, ...] = (
        r"^python -m pytest\b",
        r"^radon cc\b",
        r"^lint-imports\b",
        r"^git (status|diff)\b"
    )
    rutas_protegidas: Tuple[str, ...] = ("tests/", "tests\\")
    max_pasos: int = 15
    aprobar_edicion: Optional[Callable[[dict], bool]] = None

    def evaluar(self, accion: str, args: dict, paso: int) -> Decision:
        if paso > self.max_pasos:
            return Decision(False, f"Se alcanzó el máximo de {self.max_pasos} pasos")
        if accion not in self.herramientas_permitidas:
            return Decision(False, f"Herramienta no permitida: {accion}")
        if accion == "ejecutar_comando":
            cmd = args.get("comando", "")
            if not any(re.search(p, cmd) for p in self.comandos_permitidos):
                return Decision(False, f"Comando fuera de la lista permitida: {cmd!r}")
        if accion == "editar_archivo":
            ruta = str(args.get("ruta", "")).replace("\\", "/")
            for prot in self.rutas_protegidas:
                if ruta.startswith(prot.replace("\\", "/")):
                    return Decision(False, f"Ruta protegida: {ruta}")
            if self.aprobar_edicion and not self.aprobar_edicion(args):
                return Decision(False, "El revisor humano rechazó la edición")
        return Decision(True)
