"""Ejecución de la Variante A: Agente único resolviendo el Issue #02."""

import argparse
import pathlib
import sys

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

    trayectoria_path = raiz_repo / "agentes" / "trayectorias" / "ejecutor_issue_02_unico.json"
    traza_path = raiz_repo / "agentes" / "trazas" / "ejecutor_issue_02_unico.jsonl"
    mmd_path = raiz_repo / "agentes" / "trazas" / "ejecutor_issue_02_unico.mmd"

    if interactivo:
        modelo = ModeloInteractivo(grabador_archivo=trayectoria_path)
    else:
        modelo = ModeloGrabado(trayectoria_path)

    objetivo = (
        "Resuelve el issue issues/ISSUE-02.md. Explora el repositorio, reproduce el error con las pruebas, "
        "localiza la causa raíz, edita el archivo correspondiente y verifica que todas las pruebas pasen en verde.\n"
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

    print(f"=== INICIANDO VARIANTE A (Agente Único - Modo: {'Interactivo' if interactivo else 'Grabado'}) ===")
    resumen = agente.ejecutar()
    print("\n=== AGENTE FINALIZADO ===")
    print(f"Resultado: {resumen}")

    generar_diagrama_mermaid(str(traza_path), str(mmd_path))
    print(f"Diagrama Mermaid generado en: {mmd_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ejecutor único para resolver Issue #02")
    parser.add_argument("--interactivo", action="store_true", help="Modo interactivo con asistente LLM")
    args = parser.parse_args()
    resolver(interactivo=args.interactivo)
