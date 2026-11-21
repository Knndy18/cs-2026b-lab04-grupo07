"""Script de ejecución del agente ReAct para resolver el Issue #01 (Paso 8 y 9 de la guía)."""

import argparse
import pathlib
import subprocess
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

    trayectoria_path = raiz_repo / "agentes" / "trayectorias" / "ejecutor_issue_01.json"
    traza_path = raiz_repo / "agentes" / "trazas" / "ejecutor_issue_01.jsonl"
    mmd_path = raiz_repo / "agentes" / "trazas" / "ejecutor_issue_01.mmd"

    if interactivo:
        modelo = ModeloInteractivo(grabador_archivo=trayectoria_path)
    else:
        modelo = ModeloGrabado(trayectoria_path)

    objetivo = (
        "Resuelve el issue issues/ISSUE-01.md. Explora el repositorio, reproduce el error con las pruebas, "
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

    print(f"=== INICIANDO AGENTE REACT (Modo: {'Interactivo' if interactivo else 'Grabado'}) ===")
    resumen = agente.ejecutar()
    print("\n=== AGENTE FINALIZADO ===")
    print(f"Resultado: {resumen}")

    # Generar diagrama Mermaid
    diag_mmd = generar_diagrama_mermaid(str(traza_path), str(mmd_path))
    print(f"Diagrama Mermaid generado en: {mmd_path}")

    # Generar diagrama PlantUML de secuencia y exportar a PNG
    puml_path = raiz_repo / "agentes" / "trazas" / "ejecutor_issue_01.puml"
    png_path = raiz_repo / "agentes" / "trazas" / "ejecutor_issue_01.png"
    generar_diagrama_puml(diag_mmd, puml_path, png_path)


def generar_diagrama_puml(diag_mmd: str, puml_path: pathlib.Path, png_path: pathlib.Path) -> None:
    """Convierte el diagrama Mermaid a PlantUML y lo compila a PNG mediante plantuml.jar."""
    lineas_puml = [
        "@startuml ejecutor_issue_01",
        "autonumber",
        "skinparam responseMessageBelowArrow true",
        "skinparam defaultFontName sans-serif",
        "skinparam sequenceMessageAlign center",
        "actor Humano as \"Humano\"",
        "participant Ejecutor as \"Ejecutor (actor)\"",
        "participant Politica as \"Política (guardrails)\"",
        "participant Herramientas as \"Herramientas (sandbox)\"",
        ""
    ]

    for linea in diag_mmd.splitlines():
        linea = linea.strip()
        if not linea or linea.startswith(("sequenceDiagram", "autonumber", "actor", "participant")):
            continue
        if "-->>" in linea:
            partes = linea.split("-->>", 1)
            origen = partes[0].strip()
            dest, msg = partes[1].split(":", 1)
            msg_clean = msg.strip().replace('"', '').replace("'", "")
            lineas_puml.append(f'{origen} --> {dest.strip()} : {msg_clean}')
        elif "->>" in linea:
            partes = linea.split("->>", 1)
            origen = partes[0].strip()
            dest, msg = partes[1].split(":", 1)
            msg_clean = msg.strip().replace('"', '').replace("'", "")
            lineas_puml.append(f'{origen} -> {dest.strip()} : {msg_clean}')
        elif "-x" in linea:
            partes = linea.split("-x", 1)
            origen = partes[0].strip()
            dest, msg = partes[1].split(":", 1)
            msg_clean = msg.strip().replace('"', '').replace("'", "")
            lineas_puml.append(f'{origen} -[#red]x {dest.strip()} : {msg_clean}')
        elif "--x" in linea:
            partes = linea.split("--x", 1)
            origen = partes[0].strip()
            dest, msg = partes[1].split(":", 1)
            msg_clean = msg.strip().replace('"', '').replace("'", "")
            lineas_puml.append(f'{origen} --[#red]x {dest.strip()} : {msg_clean}')

    lineas_puml.append("@enduml\n")
    puml_path.parent.mkdir(parents=True, exist_ok=True)
    puml_path.write_text("\n".join(lineas_puml), encoding="utf-8")

    jar_path = pathlib.Path(r"C:\Users\ASUS\.vscode\extensions\jebbs.plantuml-2.18.1\plantuml.jar")
    if jar_path.is_file():
        try:
            cmd = ["java", "-jar", str(jar_path), "-tpng", str(puml_path), "-o", str(png_path.parent)]
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"Diagrama PNG renderizado exitosamente en: {png_path}")
        except Exception as err:
            print(f"Advertencia al renderizar PlantUML PNG: {err}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ejecutor ReAct para resolver Issue #01")
    parser.add_argument("--interactivo", action="store_true", help="Modo interactivo con asistente LLM")
    args = parser.parse_args()
    resolver(interactivo=args.interactivo)
