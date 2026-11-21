"""Modelos de razonamiento e interfaces de ejecución (Paso 7 de la guía)."""

import abc
import json
import pathlib
from typing import Any, Dict, List, Union


class Modelo(abc.ABC):
    @abc.abstractmethod
    def decidir(self, historial: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Recibe el historial conversacional y devuelve una decisión en formato JSON."""
        pass


class ModeloGrabado(Modelo):
    """Reproduce una trayectoria de decisiones previamente grabadas (ideal para pruebas y CI)."""
    def __init__(self, ruta_o_decisiones: Union[str, pathlib.Path, List[Dict[str, Any]]]):
        if isinstance(ruta_o_decisiones, (str, pathlib.Path)):
            p = pathlib.Path(ruta_o_decisiones)
            self.decisiones = json.loads(p.read_text(encoding="utf-8"))
        else:
            self.decisiones = list(ruta_o_decisiones)
        self.idx = 0

    def decidir(self, historial: List[Dict[str, Any]]) -> Dict[str, Any]:
        if self.idx >= len(self.decisiones):
            return {
                "pensamiento": "No hay más decisiones grabadas en la trayectoria.",
                "final": "Terminado: fin de decisiones grabadas."
            }
        d = self.decisiones[self.idx]
        self.idx += 1
        return d


class ModeloInteractivo(Modelo):
    """Permite interactuar con un asistente LLM copiando el contexto y pegando el JSON devuelto."""
    def __init__(self, grabador_archivo: Union[str, pathlib.Path, None] = None):
        self.grabador_archivo = pathlib.Path(grabador_archivo) if grabador_archivo else None
        self.grabadas: List[Dict[str, Any]] = []

    def decidir(self, historial: List[Dict[str, Any]]) -> Dict[str, Any]:
        ultimo = historial[-1]
        print("\n======================= PROMPT PARA ASISTENTE =======================")
        print(f"Rol: {ultimo['role']}")
        contenido = str(ultimo["content"])
        if len(contenido) > 1000:
            print(contenido[:500] + f"\n... [truncado {len(contenido)-1000} caracteres] ...\n" + contenido[-500:])
        else:
            print(contenido)
        print("=====================================================================")

        while True:
            try:
                linea = input("\nPegue la respuesta JSON del asistente (pensamiento + accion/final): ")
                if not linea.strip():
                    continue
                d = json.loads(linea)
                self.grabadas.append(d)
                if self.grabador_archivo:
                    self.grabador_archivo.parent.mkdir(parents=True, exist_ok=True)
                    self.grabador_archivo.write_text(
                        json.dumps(self.grabadas, indent=2, ensure_ascii=False),
                        encoding="utf-8"
                    )
                return d
            except Exception as e:
                print(f"Error parseando JSON: {e}. Intente nuevamente.")
