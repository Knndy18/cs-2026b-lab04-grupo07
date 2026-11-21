"""Script de ejecución del agente ReAct para resolver el Issue #03 con mapa_repo y memoria de notas (E4)."""

import argparse
import json
import pathlib
import sys

# Asegurar que la raíz del proyecto esté en sys.path
raiz_repo = pathlib.Path(__file__).resolve().parent.parent
if str(raiz_repo) not in sys.path:
    sys.path.insert(0, str(raiz_repo))

from agentes.agente.herramientas import Herramientas
from agentes.agente.modelo import ModeloGrabado, ModeloInteractivo
from agentes.agente.nucleo import Agente
from agentes.agente.politica import Politica
from agentes.agente.traza import generar_diagrama_mermaid


def resolver(interactivo: bool = False) -> None:
    h = Herramientas(raiz=raiz_repo)
    politica = Politica(max_pasos=15)

    trayectoria_path = raiz_repo / "agentes" / "trayectorias" / "ejecutor_issue_03.json"
    traza_path = raiz_repo / "agentes" / "trazas" / "ejecutor_issue_03.jsonl"
    mmd_path = raiz_repo / "agentes" / "trazas" / "ejecutor_issue_03.mmd"

    if interactivo:
        modelo = ModeloInteractivo(grabador_archivo=trayectoria_path)
    else:
        modelo = ModeloGrabado(trayectoria_path)

    objetivo = (
        "Resuelve el issue issues/ISSUE-03.md. Explora la estructura de clases y funciones con mapa_repo, "
        "registra hipótesis con anotar y consúltalas con leer_notas. Reproduce el fallo contable con las pruebas, "
        "edita src/pedidos/liquidacion.py para subsanar el descuadre de céntimos y verifica que todas las pruebas pasen en verde.\n"
        f"Herramientas disponibles:\n{h.catalogo()}"
    )

    agente = Agente(
        rol="ejecutor",
        modelo=modelo,
        herramientas=h,
        politica=politica,
        objetivo=objetivo,
        traza_archivo=str(traza_path)
    )

    print(f"=== INICIANDO AGENTE REACT ISSUE #03 (Modo: {'Interactivo' if interactivo else 'Grabado'}) ===")
    resumen = agente.ejecutar()
    print("\n=== AGENTE FINALIZADO ===")
    print(f"Resultado: {resumen}")

    # Generar diagrama Mermaid
    generar_diagrama_mermaid(str(traza_path), str(mmd_path))
    print(f"Diagrama Mermaid generado en: {mmd_path}")

    # Calcular métricas del agente
    contexto_chars = sum(len(msg["content"]) for msg in agente.historial)
    pasos = len([e for e in agente.eventos if e["tipo"] in ("accion", "final")])
    acciones = len([e for e in agente.eventos if e["tipo"] == "accion"])
    bloqueadas = len([e for e in agente.eventos if e.get("bloqueada", False)])
    print(f"Métricas E4 Issue #03: Pasos={pasos}, Acciones={acciones}, Bloqueadas={bloqueadas}, Contexto={contexto_chars} chars")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ejecutor ReAct para resolver Issue #03")
    parser.add_argument("--interactivo", action="store_true", help="Modo interactivo con asistente LLM")
    args = parser.parse_args()
    resolver(interactivo=args.interactivo)
