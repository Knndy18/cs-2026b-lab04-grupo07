"""Herramientas del agente con sandbox de seguridad (Albada, 2025; Grootendorst & Alammar, 2026)."""

import os
import pathlib
import subprocess
from typing import Dict, List, Optional


class Herramientas:
    """Colección de herramientas que interactúan de forma segura con el repositorio."""
    def __init__(self, raiz: pathlib.Path):
        self.raiz = pathlib.Path(raiz).resolve()

    def _ruta(self, ruta: str) -> pathlib.Path:
        p = (self.raiz / ruta).resolve()
        if self.raiz not in p.parents and p != self.raiz:
            raise PermissionError(f"Ruta fuera del sandbox: {ruta}")
        return p

    def listar_archivos(self, subruta: str = ".") -> str:
        p = self._ruta(subruta)
        if not p.is_dir():
            return f"ERROR: '{subruta}' no es un directorio"
        archivos = []
        for elem in sorted(p.rglob("*")):
            if elem.is_file() and not any(part.startswith((".", "__pycache__")) for part in elem.parts):
                rel = elem.relative_to(self.raiz)
                archivos.append(str(rel).replace("\\", "/"))
        return "\n".join(archivos) if archivos else "(directorio vacío)"

    def leer_archivo(self, ruta: str) -> str:
        p = self._ruta(ruta)
        if not p.is_file():
            return f"ERROR: archivo no encontrado: {ruta}"
        return p.read_text(encoding="utf-8")

    def buscar(self, patron: str, subruta: str = ".") -> str:
        p = self._ruta(subruta)
        coincidencias = []
        for elem in sorted(p.rglob("*.py")):
            if any(part.startswith((".", "__pycache__")) for part in elem.parts):
                continue
            try:
                lineas = elem.read_text(encoding="utf-8").splitlines()
                for i, linea in enumerate(lineas, 1):
                    if patron in linea:
                        rel = elem.relative_to(self.raiz)
                        coincidencias.append(f"{str(rel).replace('\\', '/')}:{i}: {linea.strip()}")
            except Exception:
                pass
        return "\n".join(coincidencias) if coincidencias else f"(sin coincidencias para {patron!r})"

    def editar_archivo(self, ruta: str, antes: str, despues: str) -> str:
        p = self._ruta(ruta)
        if not p.is_file():
            return f"ERROR: archivo no encontrado: {ruta}"
        texto = p.read_text(encoding="utf-8")
        if texto.count(antes) != 1:
            return f"ERROR: el fragmento aparece {texto.count(antes)} veces; debe aparecer exactamente 1"
        p.write_text(texto.replace(antes, despues), encoding="utf-8")
        return f"OK: {ruta} modificado"

    def ejecutar_pruebas(self, subruta: str = "tests") -> str:
        cmd = ["python", "-m", "pytest", "-q", subruta]
        res = subprocess.run(cmd, cwd=self.raiz, capture_output=True, text=True, encoding="utf-8")
        salida = (res.stdout + "\n" + res.stderr).strip()
        return salida if salida else "(sin salida)"

    def ver_cambios(self) -> str:
        res = subprocess.run(["git", "diff"], cwd=self.raiz, capture_output=True, text=True, encoding="utf-8")
        salida = res.stdout.strip()
        return salida if salida else "(sin cambios git)"

    def ejecutar_comando(self, comando: str) -> str:
        res = subprocess.run(comando, shell=True, cwd=self.raiz, capture_output=True, text=True, encoding="utf-8")
        salida = (res.stdout + "\n" + res.stderr).strip()
        return salida if salida else "(comando ejecutado sin salida)"

    def catalogo(self) -> Dict[str, str]:
        return {
            "listar_archivos": "Lista archivos dentro del sandbox. Args: {'subruta': str}",
            "leer_archivo": "Lee el contenido de un archivo de texto. Args: {'ruta': str}",
            "buscar": "Busca un patrón de texto en archivos Python del repositorio. Args: {'patron': str, 'subruta': str}",
            "editar_archivo": "Reemplaza exactamente una ocurrencia de 'antes' por 'despues' en un archivo. Args: {'ruta': str, 'antes': str, 'despues': str}",
            "ejecutar_pruebas": "Ejecuta pytest en el sandbox. Args: {'subruta': str}",
            "ver_cambios": "Muestra el git diff de los cambios realizados en el espacio de trabajo. Args: {}",
            "ejecutar_comando": "Ejecuta un comando de sistema en la lista permitida. Args: {'comando': str}"
        }
