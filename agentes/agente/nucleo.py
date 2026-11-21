"""Núcleo del agente: el bucle ReAct como máquina de estados (Paso 3 de la guía)."""

import json
import pathlib
import time
from typing import Any, Dict, List

from agentes.agente.contrato import validar_decision
from agentes.agente.herramientas import Herramientas
from agentes.agente.modelo import Modelo
from agentes.agente.politica import Politica


class Agente:
    """Implementa el bucle ReAct coordinado por una máquina de estados finitos."""
    def __init__(
        self,
        rol: str,
        modelo: Modelo,
        herramientas: Herramientas,
        politica: Politica,
        objetivo: str,
        traza_archivo: str = "trazas/agente.jsonl"
    ):
        self.rol = rol
        self.modelo = modelo
        self.h = herramientas
        self.politica = politica
        self.objetivo = objetivo
        self.traza_archivo = traza_archivo
        self.historial: List[Dict[str, Any]] = [{"role": "user", "content": objetivo}]
        self.eventos: List[Dict[str, Any]] = []
        self._t0: float = 0.0

    def _registrar(
        self,
        tipo: str,
        estado: str,
        paso: int = 0,
        pensamiento: str = "",
        accion: str = "",
        args: dict = None,
        observacion: str = "",
        texto: str = "",
        bloqueada: bool = False
    ) -> None:
        if args is None:
            args = {}
        evento = {
            "agente": self.rol,
            "tipo": tipo,
            "estado": estado,
            "paso": paso,
            "t_ms": round((time.perf_counter() - self._t0) * 1000, 1),
            "pensamiento": pensamiento,
            "accion": accion,
            "args": args,
            "observacion": observacion,
            "texto": texto,
            "bloqueada": bloqueada
        }
        self.eventos.append(evento)

    def ejecutar(self) -> str:
        self._t0 = time.perf_counter()
        self._registrar(tipo="objetivo", estado="INICIO", texto=self.historial[0]["content"])
        conocidas = set(self.h.catalogo().keys())

        for paso in range(1, self.politica.max_pasos + 2):
            d = self.modelo.decidir(self.historial)  # Estado: DECIDIENDO
            self.historial.append({"role": "assistant", "content": json.dumps(d, ensure_ascii=False)})

            ok, motivo = validar_decision(d, conocidas)  # Estado: VALIDANDO_CONTRATO
            if not ok:
                obs = f"ERROR DE CONTRATO: {motivo}. Responda solo con el JSON del protocolo."
                self._registrar(
                    tipo="accion",
                    estado="CONTRATO_INVALIDO",
                    paso=paso,
                    pensamiento=str(d.get("pensamiento", str(d)))[:200],
                    accion="(ninguna)",
                    args={},
                    observacion=obs,
                    bloqueada=True
                )
            elif "final" in d:
                self._registrar(
                    tipo="final",
                    estado="FINALIZADO",
                    paso=paso,
                    pensamiento=d["pensamiento"],
                    texto=d["final"]
                )
                break
            else:
                accion, args = d["accion"], d.get("args", {})
                veredicto = self.politica.evaluar(accion, args, paso)  # Estado: EVALUANDO_POLITICA
                if veredicto.permitido:
                    try:
                        obs = getattr(self.h, accion)(**args)  # Estado: EJECUTANDO
                    except Exception as e:
                        obs = f"ERROR: {type(e).__name__}: {e}"
                    self._registrar(
                        tipo="accion",
                        estado="OBSERVANDO",
                        paso=paso,
                        pensamiento=d["pensamiento"],
                        accion=accion,
                        args=args,
                        observacion=obs[:600],
                        bloqueada=False
                    )
                else:
                    obs = f"BLOQUEADO POR LA POLÍTICA: {veredicto.motivo}"
                    limite = "máximo" in veredicto.motivo
                    self._registrar(
                        tipo="accion",
                        estado="LIMITE_ALCANZADO" if limite else "BLOQUEADO",
                        paso=paso,
                        pensamiento=d["pensamiento"],
                        accion=accion,
                        args=args,
                        observacion=obs,
                        bloqueada=True
                    )
                    if limite:
                        break

            self.historial.append({"role": "user", "content": f"Observación: {obs}"})  # OBSERVANDO -> DECIDIENDO

        # Persistir traza estructurada en JSONL
        p_traza = pathlib.Path(self.traza_archivo)
        p_traza.parent.mkdir(parents=True, exist_ok=True)
        with open(p_traza, "w", encoding="utf-8") as f:
            for e in self.eventos:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")

        return self.eventos[-1].get("texto", "(sin respuesta final)")
