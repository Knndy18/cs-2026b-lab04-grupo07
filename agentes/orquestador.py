"""Orquestador multiagente: Planificador + bucle Actor-Crítico (Paso 8 de la guía)."""

import argparse
import pathlib
import sys
from typing import List

# Asegurar que la raíz del proyecto esté en sys.path
raiz_repo = pathlib.Path(__file__).resolve().parent.parent
if str(raiz_repo) not in sys.path:
    sys.path.insert(0, str(raiz_repo))

from agentes.agente.herramientas import Herramientas
from agentes.agente.modelo import ModeloGrabado, ModeloInteractivo
from agentes.agente.nucleo import Agente
from agentes.agente.politica import Politica, pedir_aprobacion_humana
from agentes.agente.traza import generar_diagrama_mermaid

MAX_RONDAS: int = 2


def orquestar(interactivo: bool = False, aprobacion_humana: bool = False) -> None:
    h = Herramientas(raiz=raiz_repo)
    print("=== INICIANDO ORQUESTADOR MULTIAGENTE (ACTOR-CRÍTICO) - ISSUE #02 ===")

    # 1. Fase de Planificación (Gestor)
    tray_plan = raiz_repo / "agentes" / "trayectorias" / "planificador_issue_02.json"
    traza_plan = raiz_repo / "agentes" / "trazas" / "planificador_issue_02.jsonl"
    mmd_plan = raiz_repo / "agentes" / "trazas" / "planificador_issue_02.mmd"

    mod_plan = ModeloInteractivo(grabador_archivo=tray_plan) if interactivo else ModeloGrabado(tray_plan)
    pol_plan = Politica(
        herramientas_permitidas={"leer_archivo", "buscar", "listar_archivos", "mapa_repo", "leer_notas"},
        max_pasos=6
    )

    planificador = Agente(
        rol="planificador",
        modelo=mod_plan,
        herramientas=h,
        politica=pol_plan,
        objetivo=(
            "Analiza el issue issues/ISSUE-02.md e inspecciona los archivos pertinentes para definir un plan de trabajo "
            "claro y acotado para el agente ejecutor.\n"
            f"Herramientas disponibles: {h.catalogo()}"
        ),
        traza_archivo=str(traza_plan)
    )

    print("\n--- FASE 1: PLANIFICADOR (Gestor) ---")
    plan = planificador.ejecutar()
    print(f"PLAN ESTRUCTURADO:\n{plan}\n")
    generar_diagrama_mermaid(str(traza_plan), str(mmd_plan))

    # 2. Bucle Actor-Crítico (Ejecutor y Revisor)
    retro = ""
    agentes_totales: List[Agente] = [planificador]
    ronda_final = 1

    fn_aprobacion = pedir_aprobacion_humana if aprobacion_humana else None

    for ronda in range(1, MAX_RONDAS + 1):
        ronda_final = ronda
        sufijo = f"_r{ronda}"
        print(f"\n==========================================")
        print(f"           RONDA ACTOR-CRÍTICO {ronda}    ")
        print(f"==========================================")

        # Ejecutor (Actor)
        tray_ejec = raiz_repo / "agentes" / "trayectorias" / f"ejecutor_issue_02{sufijo}.json"
        traza_ejec = raiz_repo / "agentes" / "trazas" / f"ejecutor_issue_02{sufijo}.jsonl"
        mmd_ejec = raiz_repo / "agentes" / "trazas" / f"ejecutor_issue_02{sufijo}.mmd"

        mod_ejec = ModeloInteractivo(grabador_archivo=tray_ejec) if interactivo else ModeloGrabado(tray_ejec)
        pol_ejec = Politica(max_pasos=12, aprobar_edicion=fn_aprobacion)

        obj_ejec = (
            f"Resuelve ISSUE-02.md siguiendo este plan de trabajo:\n{plan}\n"
            f"{retro}"
            f"Herramientas disponibles:\n{h.catalogo()}"
        )

        ejecutor = Agente(
            rol="ejecutor",
            modelo=mod_ejec,
            herramientas=h,
            politica=pol_ejec,
            objetivo=obj_ejec,
            traza_archivo=str(traza_ejec)
        )

        resumen_ejec = ejecutor.ejecutar()
        generar_diagrama_mermaid(str(traza_ejec), str(mmd_ejec))
        print(f"\n[EJECUTOR (Ronda {ronda})]:\n{resumen_ejec}\n")

        # Revisor (Crítico de solo lectura - mínimo privilegio)
        tray_rev = raiz_repo / "agentes" / "trayectorias" / f"revisor_issue_02{sufijo}.json"
        traza_rev = raiz_repo / "agentes" / "trazas" / f"revisor_issue_02{sufijo}.jsonl"
        mmd_rev = raiz_repo / "agentes" / "trazas" / f"revisor_issue_02{sufijo}.mmd"

        mod_rev = ModeloInteractivo(grabador_archivo=tray_rev) if interactivo else ModeloGrabado(tray_rev)
        pol_rev = Politica(
            herramientas_permitidas={"ver_cambios", "leer_archivo", "buscar", "ejecutar_pruebas", "leer_notas"},
            max_pasos=8
        )

        obj_rev = (
            f"Revisa exhaustivamente la modificación propuesta por el ejecutor para resolver el ISSUE-02.md.\n"
            f"Verifica la corrección de las pruebas, calidad de código y ausencia de regresiones.\n"
            f"Responde APROBADO... o CAMBIOS SOLICITADOS...\n"
            f"Resumen del ejecutor:\n{resumen_ejec}"
        )

        revisor = Agente(
            rol="revisor",
            modelo=mod_rev,
            herramientas=h,
            politica=pol_rev,
            objetivo=obj_rev,
            traza_archivo=str(traza_rev)
        )

        veredicto = revisor.ejecutar()
        generar_diagrama_mermaid(str(traza_rev), str(mmd_rev))
        print(f"\n[REVISOR (Ronda {ronda})]:\n{veredicto}\n")

        agentes_totales.extend([ejecutor, revisor])

        if not veredicto.startswith("CAMBIOS SOLICITADOS"):
            print(f"El crítico ha aprobado la solución en la ronda {ronda}.")
            break

        retro = f"El revisor solicitó cambios en la ronda {ronda}:\n{veredicto}\n"

    print("\n==========================================")
    print(f"Bucle actor-crítico finalizado: {ronda_final} de {MAX_RONDAS} rondas ejecutadas.")
    print("Decisión final: HUMANO (aprobar o rechazar el Pull Request).")
    print("==========================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Orquestador multiagente para Issue #02")
    parser.add_argument("--interactivo", action="store_true", help="Modo interactivo con asistente LLM")
    parser.add_argument("--humano", action="store_true", help="Activar aprobación humana obligatoria en cada edición")
    args = parser.parse_args()
    orquestar(interactivo=args.interactivo, aprobacion_humana=args.humano)
