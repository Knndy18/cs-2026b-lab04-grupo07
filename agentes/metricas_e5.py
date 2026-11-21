"""Script para calcular métricas de coordinación multiagente en Issue #02 a partir de trazas JSONL reales (E5)."""

import json
import pathlib
from typing import Any, Dict, List


def analizar_archivo_traza(ruta: pathlib.Path) -> Dict[str, Any]:
    if not ruta.is_file():
        return {"pasos": 0, "acciones": 0, "bloqueadas": 0, "contexto": 0, "eventos": 0}

    lineas = [l for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()]
    eventos = [json.loads(l) for l in lineas]
    if not eventos:
        return {"pasos": 0, "acciones": 0, "bloqueadas": 0, "contexto": 0, "eventos": 0}

    acciones = [e for e in eventos if e.get("tipo") == "accion"]
    bloqueadas = [e for e in acciones if e.get("bloqueada", False)]
    pasos = max((e.get("paso", 0) for e in eventos), default=0)

    # Reconstrucción de contexto acumulado
    total_contexto = len(eventos[0].get("texto", ""))
    for e in eventos[1:]:
        if e.get("tipo") == "accion":
            d = {"pensamiento": e.get("pensamiento", ""), "accion": e.get("accion", ""), "args": e.get("args", {})}
            total_contexto += len(json.dumps(d, ensure_ascii=False))
            total_contexto += len("Observación: ") + len(e.get("observacion", ""))
        elif e.get("tipo") == "final":
            d = {"pensamiento": e.get("pensamiento", ""), "final": e.get("texto", "")}
            total_contexto += len(json.dumps(d, ensure_ascii=False))

    return {
        "pasos": pasos,
        "acciones": len(acciones),
        "bloqueadas": len(bloqueadas),
        "contexto": total_contexto,
        "eventos": len(eventos)
    }


def calcular_metricas() -> Dict[str, Any]:
    raiz = pathlib.Path(__file__).resolve().parent.parent
    trazas_dir = raiz / "agentes" / "trazas"

    # Variante A: Agente Único
    traza_var_a = trazas_dir / "ejecutor_issue_02_unico.jsonl"
    m_a = analizar_archivo_traza(traza_var_a)

    # Variante B: Actor-Crítico multiagente
    archivos_b = {
        "planificador": trazas_dir / "planificador_issue_02.jsonl",
        "ejecutor_r1": trazas_dir / "ejecutor_issue_02_r1.jsonl",
        "revisor_r1": trazas_dir / "revisor_issue_02_r1.jsonl",
        "ejecutor_r2": trazas_dir / "ejecutor_issue_02_r2.jsonl",
        "revisor_r2": trazas_dir / "revisor_issue_02_r2.jsonl",
    }
    m_b_detalle = {k: analizar_archivo_traza(v) for k, v in archivos_b.items()}

    total_acciones_b = sum(d["acciones"] for d in m_b_detalle.values())
    total_bloqueadas_b = sum(d["bloqueadas"] for d in m_b_detalle.values())
    total_contexto_b = sum(d["contexto"] for d in m_b_detalle.values())
    total_pasos_b = sum(d["pasos"] for d in m_b_detalle.values())

    return {
        "variante_a": {
            "rondas": 1,
            "agentes": 1,
            "pasos": m_a["pasos"],
            "acciones": m_a["acciones"],
            "bloqueadas": m_a["bloqueadas"],
            "contexto": m_a["contexto"]
        },
        "variante_b": {
            "rondas": 2,
            "agentes": 3,  # planificador, ejecutor, revisor
            "pasos": total_pasos_b,
            "acciones": total_acciones_b,
            "bloqueadas": total_bloqueadas_b,
            "contexto": total_contexto_b,
            "detalle": m_b_detalle
        }
    }


def imprimir_informe():
    res = calcular_metricas()
    va = res["variante_a"]
    vb = res["variante_b"]

    print("================================================================================")
    print("MÉTRICAS COMPARATIVAS REALES: VARIANTE A (ÚNICO) VS VARIANTE B (ACTOR-CRÍTICO)")
    print("================================================================================")
    print(f"{'Métrica':<38} | {'Variante A (Único)':<20} | {'Variante B (Actor-Crítico)':<25}")
    print("-" * 88)
    print(f"{'Rondas de coordinación':<38} | {va['rondas']:<20} | {vb['rondas']:<25}")
    print(f"{'Agentes involucrados':<38} | {va['agentes']:<20} | {vb['agentes']:<25}")
    print(f"{'Acciones totales':<38} | {va['acciones']:<20} | {vb['acciones']:<25}")
    print(f"{'Acciones bloqueadas por política':<38} | {va['bloqueadas']:<20} | {vb['bloqueadas']:<25}")
    print(f"{'Contexto total acumulado (chars)':<38} | {va['contexto']:<20} | {vb['contexto']:<25}")
    print(f"{'Pasos totales acumulados':<38} | {va['pasos']:<20} | {vb['pasos']:<25}")
    print("-" * 88)
    print("\nDesglose de contexto y acciones por agente en Variante B:")
    for rol, det in vb["detalle"].items():
        print(f"  - {rol:<15}: {det['acciones']} acciones, {det['pasos']} pasos, {det['contexto']} chars")
    print("================================================================================")


if __name__ == "__main__":
    imprimir_informe()
