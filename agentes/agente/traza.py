"""Generador de diagramas de secuencia Mermaid a partir de trazas JSONL (Paso 9 de la guía)."""

import json
import pathlib
import sys
from typing import List


def generar_diagrama_mermaid(traza_jsonl_path: str, salida_mmd_path: str = None) -> str:
    """Lee un archivo de traza JSONL y produce un diagrama de secuencia Mermaid válido."""
    p = pathlib.Path(traza_jsonl_path)
    if not p.is_file():
        raise FileNotFoundError(f"Archivo de traza no encontrado: {traza_jsonl_path}")

    eventos = [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]

    lineas_mmd: List[str] = [
        "sequenceDiagram",
        "    autonumber",
        "    actor Humano",
        "    participant Planificador as Planificador (gestor)",
        "    participant Ejecutor as Ejecutor (actor)",
        "    participant Politica as Política (guardrails)",
        "    participant Herramientas as Herramientas (sandbox)"
    ]

    for e in eventos:
        tipo = e.get("tipo")
        estado = e.get("estado")
        agente = "Ejecutor" if e.get("agente") in ("ejecutor", "agente") else (e.get("agente") or "Ejecutor")
        accion = e.get("accion", "")
        args = e.get("args", {})
        obs = e.get("observacion", "").replace("\n", " ").replace('"', "'")
        bloqueada = e.get("bloqueada", False)

        if len(obs) > 55:
            obs = obs[:52] + "..."

        if tipo == "objetivo":
            lineas_mmd.append(f"    Humano->>Ejecutor: Objetivo: Resolver incidencia")
        elif estado == "CONTRATO_INVALIDO":
            lineas_mmd.append(f"    Ejecutor--xPolitica: Decisión inválida (violación de contrato)")
            lineas_mmd.append(f"    Politica-->>Ejecutor: {obs}")
        elif bloqueada:
            args_str = json.dumps(args, ensure_ascii=False).replace('"', "'")
            lineas_mmd.append(f"    {agente}-xPolitica: {accion}({args_str})")
            lineas_mmd.append(f"    Politica-->>{agente}: {obs}")
        elif tipo == "accion":
            args_str = json.dumps(args, ensure_ascii=False).replace('"', "'")
            if len(args_str) > 40:
                args_str = args_str[:37] + "...}"
            lineas_mmd.append(f"    {agente}->>Herramientas: {accion}({args_str})")
            lineas_mmd.append(f"    Herramientas-->>{agente}: {obs}")
        elif tipo == "final":
            texto = e.get("texto", "").replace("\n", " ").replace('"', "'")
            if len(texto) > 60:
                texto = texto[:57] + "..."
            lineas_mmd.append(f"    {agente}-->>Humano: Respuesta final: {texto}")

    diagrama = "\n".join(lineas_mmd) + "\n"

    if salida_mmd_path:
        p_salida = pathlib.Path(salida_mmd_path)
        p_salida.parent.mkdir(parents=True, exist_ok=True)
        p_salida.write_text(diagrama, encoding="utf-8")

    return diagrama


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python agente/traza.py <ruta_traza.jsonl> [ruta_salida.mmd]")
        sys.exit(1)
    traza_in = sys.argv[1]
    mmd_out = sys.argv[2] if len(sys.argv) > 2 else traza_in.replace(".jsonl", ".mmd")
    diag = generar_diagrama_mermaid(traza_in, mmd_out)
    print(f"Diagrama Mermaid generado exitosamente en: {mmd_out}")
