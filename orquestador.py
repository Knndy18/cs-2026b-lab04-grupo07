"""Wrapper raíz para ejecutar agentes/orquestador.py directamente desde la raíz del proyecto."""

import sys
import pathlib

raiz = pathlib.Path(__file__).resolve().parent
if str(raiz) not in sys.path:
    sys.path.insert(0, str(raiz))

from agentes.orquestador import orquestar

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Orquestador multiagente para Issue #02")
    parser.add_argument("--interactivo", action="store_true", help="Modo interactivo con asistente LLM")
    parser.add_argument("--humano", action="store_true", help="Activar aprobación humana obligatoria en cada edición")
    args = parser.parse_args()
    orquestar(interactivo=args.interactivo, aprobacion_humana=args.humano)
