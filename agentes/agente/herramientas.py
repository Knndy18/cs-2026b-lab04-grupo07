"""Herramientas del agente con sandbox de seguridad (Albada, 2025; Grootendorst & Alammar, 2026)."""

import ast
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
                        rel_posix = str(rel).replace("\\", "/")
                        coincidencias.append(f"{rel_posix}:{i}: {linea.strip()}")
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
        res = subprocess.run(cmd, cwd=self.raiz, capture_output=True, text=True, encoding="utf-8", errors="replace")
        salida = (res.stdout + "\n" + res.stderr).strip()
        return salida if salida else "(sin salida)"

    def ver_cambios(self) -> str:
        res = subprocess.run(["git", "diff"], cwd=self.raiz, capture_output=True, text=True, encoding="utf-8", errors="replace")
        salida = res.stdout.strip()
        return salida if salida else "(sin cambios git)"

    def ejecutar_comando(self, comando: str) -> str:
        res = subprocess.run(comando, shell=True, cwd=self.raiz, capture_output=True, text=True, encoding="utf-8", errors="replace")
        salida = (res.stdout + "\n" + res.stderr).strip()
        return salida if salida else "(comando ejecutado sin salida)"

    def mapa_repo(self, subruta: str = ".", max_chars: int = 4000) -> str:
        """Recorre archivos .py en el sandbox y devuelve clases y funciones con sus firmas usando ast."""
        p = self._ruta(subruta)
        if not p.is_dir():
            return f"ERROR: '{subruta}' no es un directorio"

        ignorar = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache"}
        salida_lineas = []

        for raiz_dir, dirs, archivos in os.walk(p):
            dirs[:] = [d for d in sorted(dirs) if d not in ignorar and not d.startswith(".")]
            archivos_py = [f for f in sorted(archivos) if f.endswith(".py")]
            if not archivos_py:
                continue

            rel_dir = pathlib.Path(raiz_dir).resolve().relative_to(self.raiz)
            rel_dir_str = str(rel_dir).replace("\\", "/")
            salida_lineas.append(f"[{rel_dir_str}]")

            for arch in archivos_py:
                ruta_arch = pathlib.Path(raiz_dir) / arch
                rel_arch = ruta_arch.resolve().relative_to(self.raiz)
                salida_lineas.append(f"  {arch}:")
                try:
                    contenido = ruta_arch.read_text(encoding="utf-8")
                    tree = ast.parse(contenido, filename=str(rel_arch))
                except SyntaxError as e:
                    salida_lineas.append(f"    [Error de sintaxis: {e.msg} (línea {e.lineno})]")
                    continue
                except Exception as e:
                    salida_lineas.append(f"    [Error de lectura: {e}]")
                    continue

                elementos = []
                for nodo in tree.body:
                    if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        firma = f"def {nodo.name}({ast.unparse(nodo.args)})"
                        if nodo.returns:
                            firma += f" -> {ast.unparse(nodo.returns)}"
                        elementos.append(f"    {firma}")
                    elif isinstance(nodo, ast.ClassDef):
                        bases_str = f"({', '.join(ast.unparse(b) for b in nodo.bases)})" if nodo.bases else ""
                        elementos.append(f"    class {nodo.name}{bases_str}:")
                        for subnodo in nodo.body:
                            if isinstance(subnodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                sub_firma = f"def {subnodo.name}({ast.unparse(subnodo.args)})"
                                if subnodo.returns:
                                    sub_firma += f" -> {ast.unparse(subnodo.returns)}"
                                elementos.append(f"      {sub_firma}")

                if elementos:
                    salida_lineas.extend(elementos)
                else:
                    salida_lineas.append("    (sin clases ni funciones)")

        resultado = "\n".join(salida_lineas) if salida_lineas else "(repositorio sin archivos .py)"
        if len(resultado) > max_chars:
            resultado = resultado[:max_chars] + f"\n... [salida truncada a {max_chars} caracteres]"
        return resultado

    def anotar(self, texto: str) -> str:
        """Agrega una nota numerada en notas.md dentro del sandbox."""
        if not isinstance(texto, str) or not texto.strip():
            return "ERROR: 'texto' debe ser una cadena no vacía"
        p = self._ruta("notas.md")
        num = 1
        if p.is_file():
            lineas = [l for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
            num = len(lineas) + 1
        nueva_linea = f"{num}. {texto.strip()}\n"
        with open(p, "a", encoding="utf-8") as f:
            f.write(nueva_linea)
        return f"OK: nota {num} registrada en notas.md"

    def leer_notas(self) -> str:
        """Devuelve el contenido acumulado en notas.md dentro del sandbox o mensaje si no hay notas."""
        p = self._ruta("notas.md")
        if not p.is_file():
            return "(sin notas registradas)"
        contenido = p.read_text(encoding="utf-8").strip()
        return contenido if contenido else "(sin notas registradas)"

    def catalogo(self) -> Dict[str, str]:
        return {
            "listar_archivos": "Lista archivos dentro del sandbox. Args: {'subruta': str (opcional)}. Devuelve listado de archivos.",
            "leer_archivo": "Lee el contenido de un archivo de texto. Args: {'ruta': str}. Devuelve texto del archivo.",
            "buscar": "Busca un patrón de texto en archivos Python del repositorio. Args: {'patron': str, 'subruta': str (opcional)}. Devuelve coincidencias con línea.",
            "editar_archivo": "Reemplaza exactamente una ocurrencia de 'antes' por 'despues' en un archivo. Args: {'ruta': str, 'antes': str, 'despues': str}. Devuelve estado.",
            "ejecutar_pruebas": "Ejecuta pytest en el sandbox. Args: {'subruta': str (opcional)}. Devuelve resultado de pruebas.",
            "ver_cambios": "Muestra el git diff de los cambios realizados en el espacio de trabajo. Args: {}. Devuelve salida de git diff.",
            "ejecutar_comando": "Ejecuta un comando de sistema en la lista permitida. Args: {'comando': str}. Devuelve salida estándar y de error.",
            "mapa_repo": "Genera el mapa estructural del código fuente (.py), clases y funciones con firmas usando ast. Args: {'subruta': str (opcional)}. Devuelve mapa jerárquico.",
            "anotar": "Agrega una nota numerada de hipótesis o progreso en notas.md dentro del sandbox. Args: {'texto': str}. Devuelve confirmación.",
            "leer_notas": "Lee las notas e hipótesis acumuladas en notas.md dentro del sandbox. Args: {}. Devuelve el contenido de notas.md o mensaje si no hay notas."
        }
