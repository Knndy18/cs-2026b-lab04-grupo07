"""
fitness/disponibilidad.py
San Camilo en Línea 2.0 — Evidencia Cuantitativa de Disponibilidad [QA-03]

Escenario: Caída de Yape/Plin durante 20 min en hora pico →
           0 pedidos perdidos mediante Outbox Pattern en PostgreSQL.

Modelo:    Simulación Monte Carlo (N = 10 000 pedidos).
           Compara tres estrategias:
             A) Llamada directa (sin resiliencia) — baseline
             B) Reintentos simples con backoff exponencial
             C) Outbox Pattern + worker asíncrono (táctica elegida)

Autor: Kennedy Chirinos Rojas — Laboratorio 08
"""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass, field

# ─────────────────────────────────────────────────────────────────────────────
# 1. PARÁMETROS DEL MODELO  (extraídos de arbol.md y atam-lite.md)
# ─────────────────────────────────────────────────────────────────────────────

N_PEDIDOS       = 10_000     # N: tamaño de la simulación Monte Carlo
RANDOM_SEED     = 2026

# --- Falla del proveedor de pagos (Yape/Plin) ---
P_FALLA_PAGO    = 0.15       # probabilidad de que un pedido ocurra durante la ventana de falla
                              # (caída de 20 min en hora pico de ~2 h → ~15% del tráfico)
DURACION_FALLA_MIN = 20.0    # duración máxima de la caída [min] — QA-03
MAX_REINTENTOS  = 3          # reintentos en estrategia B
BACKOFF_BASE_S  = 30         # segundos base para backoff exponencial
MAX_ESPERA_MIN  = 15.0       # ventana de recuperación máxima aceptable [min] — QA-02

# Outbox Pattern: tiempo máximo de procesamiento tras recuperar la conexión
OUTBOX_PROC_MIN = 3.0        # máx 3 min para procesar la cola outbox — T2 / atam-lite.md


# ─────────────────────────────────────────────────────────────────────────────
# 2. ESTRUCTURAS DE DATOS
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ResultadoPedido:
    pedido_id:       int
    en_ventana_falla: bool          # True si llegó durante la caída del proveedor
    strategy:        str
    exitoso:         bool
    tiempo_proceso_min: float       # tiempo hasta confirmación final [min]
    reintentos:      int = 0


@dataclass
class ResumenSimulacion:
    strategy:           str
    n_total:            int
    n_perdidos:         int
    n_en_falla:         int
    pct_perdidos:       float
    pct_recuperados:    float        # de los que estuvieron en falla
    tiempo_medio_min:   float
    tiempo_p95_min:     float
    cumple_qa03:        bool         # 0 pedidos perdidos
    cumple_tiempo:      bool         # tiempo_p95 ≤ MAX_ESPERA_MIN


# ─────────────────────────────────────────────────────────────────────────────
# 3. ESTRATEGIAS DE RESILIENCIA
# ─────────────────────────────────────────────────────────────────────────────

def estrategia_sin_resiliencia(
    pedido_id: int,
    en_falla: bool,
    rng: random.Random,
) -> ResultadoPedido:
    """Estrategia A — Llamada directa sin manejo de fallos.

    Si el proveedor está caído, el pedido falla y se pierde.
    El tiempo de proceso es inmediato si hay conexión.
    """
    if en_falla:
        return ResultadoPedido(
            pedido_id=pedido_id,
            en_ventana_falla=True,
            strategy="A_sin_resiliencia",
            exitoso=False,
            tiempo_proceso_min=0.0,
        )
    # Tiempo de proceso normal: ~0.5–3 min (confirmación Yape en línea)
    t = rng.uniform(0.5, 3.0)
    return ResultadoPedido(
        pedido_id=pedido_id,
        en_ventana_falla=False,
        strategy="A_sin_resiliencia",
        exitoso=True,
        tiempo_proceso_min=t,
    )


def estrategia_reintentos(
    pedido_id: int,
    en_falla: bool,
    rng: random.Random,
) -> ResultadoPedido:
    """Estrategia B — Reintentos simples con backoff exponencial.

    Intenta hasta MAX_REINTENTOS veces con espera 2^i × BACKOFF_BASE_S.
    La falla persiste durante la ventana completa: si todos los reintentos
    caen dentro de ella, el pedido se pierde.
    """
    if not en_falla:
        t = rng.uniform(0.5, 3.0)
        return ResultadoPedido(
            pedido_id=pedido_id,
            en_ventana_falla=False,
            strategy="B_reintentos",
            exitoso=True,
            tiempo_proceso_min=t,
        )

    # Tiempo residual de falla al momento de llegada (uniforme [0, DURACION_FALLA])
    t_restante_falla = rng.uniform(0, DURACION_FALLA_MIN)
    t_acumulado = 0.0

    for intento in range(1, MAX_REINTENTOS + 1):
        espera_s = (2 ** intento) * BACKOFF_BASE_S + rng.uniform(-5, 5)
        espera_min = espera_s / 60.0
        t_acumulado += espera_min
        if t_acumulado >= t_restante_falla:
            # La falla terminó antes del próximo reintento → éxito
            t_extra = rng.uniform(0.5, 2.0)
            return ResultadoPedido(
                pedido_id=pedido_id,
                en_ventana_falla=True,
                strategy="B_reintentos",
                exitoso=True,
                tiempo_proceso_min=t_acumulado + t_extra,
                reintentos=intento,
            )

    # Agotó reintentos dentro de la ventana de falla → pedido perdido
    return ResultadoPedido(
        pedido_id=pedido_id,
        en_ventana_falla=True,
        strategy="B_reintentos",
        exitoso=False,
        tiempo_proceso_min=t_acumulado,
        reintentos=MAX_REINTENTOS,
    )


def estrategia_outbox(
    pedido_id: int,
    en_falla: bool,
    rng: random.Random,
) -> ResultadoPedido:
    """Estrategia C — Outbox Pattern (táctica elegida, QA-03 / atam-lite.md T2).

    El pedido siempre se persiste en PostgreSQL con estado 'PENDIENTE_PAGO'.
    Un worker Celery monitorea la tabla outbox y reintenta el cobro al
    detectar que el proveedor está disponible nuevamente.

    Garantía: 0 pedidos perdidos (el pedido siempre queda en la DB).
    Coste: confirmación diferida (consistencia eventual).
    """
    if not en_falla:
        t = rng.uniform(0.5, 2.5)
        return ResultadoPedido(
            pedido_id=pedido_id,
            en_ventana_falla=False,
            strategy="C_outbox",
            exitoso=True,
            tiempo_proceso_min=t,
        )

    # Tiempo residual de falla + tiempo de procesamiento del worker
    t_restante_falla = rng.uniform(0, DURACION_FALLA_MIN)
    t_worker_proc    = rng.uniform(0.1, OUTBOX_PROC_MIN)
    t_total          = t_restante_falla + t_worker_proc

    return ResultadoPedido(
        pedido_id=pedido_id,
        en_ventana_falla=True,
        strategy="C_outbox",
        exitoso=True,          # SIEMPRE exitoso: el pedido está en la DB
        tiempo_proceso_min=t_total,
        reintentos=1,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 4. MOTOR DE SIMULACIÓN MONTE CARLO
# ─────────────────────────────────────────────────────────────────────────────

def simular(
    strategy_fn,
    strategy_name: str,
    n: int,
    p_falla: float,
    seed: int,
) -> ResumenSimulacion:
    """Ejecuta N pedidos Monte Carlo con la estrategia dada.

    Args:
        strategy_fn:   función de estrategia a evaluar.
        strategy_name: etiqueta de la estrategia.
        n:             número de pedidos a simular.
        p_falla:       probabilidad de que un pedido llegue en ventana de falla.
        seed:          semilla para reproducibilidad.

    Returns:
        ResumenSimulacion con métricas agregadas.
    """
    rng = random.Random(seed)
    resultados: list[ResultadoPedido] = []

    for i in range(n):
        en_falla = rng.random() < p_falla
        r = strategy_fn(i, en_falla, rng)
        resultados.append(r)

    perdidos    = [r for r in resultados if not r.exitoso]
    en_falla_t  = [r for r in resultados if r.en_ventana_falla]
    recuperados = [r for r in en_falla_t if r.exitoso]
    tiempos     = sorted(r.tiempo_proceso_min for r in resultados if r.exitoso)

    n_total   = len(resultados)
    n_perdidos = len(perdidos)
    n_en_falla = len(en_falla_t)

    pct_perdidos    = (n_perdidos / n_total) * 100
    pct_recuperados = (len(recuperados) / n_en_falla * 100) if n_en_falla > 0 else 100.0
    t_medio = statistics.mean(tiempos) if tiempos else 0.0
    idx_p95 = min(int(math.ceil(0.95 * len(tiempos))) - 1, len(tiempos) - 1)
    t_p95   = tiempos[idx_p95] if tiempos else 0.0

    return ResumenSimulacion(
        strategy=strategy_name,
        n_total=n_total,
        n_perdidos=n_perdidos,
        n_en_falla=n_en_falla,
        pct_perdidos=pct_perdidos,
        pct_recuperados=pct_recuperados,
        tiempo_medio_min=t_medio,
        tiempo_p95_min=t_p95,
        cumple_qa03=(n_perdidos == 0),
        cumple_tiempo=(t_p95 <= MAX_ESPERA_MIN),
    )


# ─────────────────────────────────────────────────────────────────────────────
# 5. EJECUCIÓN Y REPORTE
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 65)
    print("  EVIDENCIA CUANTITATIVA — Disponibilidad [QA-03]")
    print("  San Camilo en Línea 2.0 — fitness/disponibilidad.py")
    print("=" * 65)
    print(f"\n  N pedidos simulados  = {N_PEDIDOS:,}")
    print(f"  P(falla proveedor)   = {P_FALLA_PAGO*100:.0f}%  (20 min caída en hora pico)")
    print(f"  Duración falla       = {DURACION_FALLA_MIN:.0f} min  [QA-03 / arbol.md]")
    print(f"  SLA: pedidos perdidos ≤ 0  |  tiempo_p95 ≤ {MAX_ESPERA_MIN:.0f} min")
    print(f"  Semilla aleatoria    = {RANDOM_SEED}\n")

    estrategias = [
        (estrategia_sin_resiliencia, "A — Sin resiliencia (baseline)",   RANDOM_SEED),
        (estrategia_reintentos,      "B — Reintentos backoff exp.",       RANDOM_SEED + 1),
        (estrategia_outbox,          "C — Outbox Pattern (elegida)",      RANDOM_SEED + 2),
    ]

    resultados: list[ResumenSimulacion] = []
    for fn, nombre, seed in estrategias:
        r = simular(fn, nombre, N_PEDIDOS, P_FALLA_PAGO, seed)
        resultados.append(r)
        print(f"{'─'*65}")
        print(f"  {r.strategy}")
        print(f"    Pedidos totales        : {r.n_total:,}")
        print(f"    Pedidos en ventana falla: {r.n_en_falla:,}  ({r.n_en_falla/r.n_total*100:.1f}%)")
        print(f"    Pedidos perdidos        : {r.n_perdidos:,}  ({r.pct_perdidos:.2f}%)")
        print(f"    Recuperados de la falla : {r.pct_recuperados:.1f}%")
        print(f"    Tiempo medio proceso   : {r.tiempo_medio_min:.2f} min")
        print(f"    Tiempo p95 proceso     : {r.tiempo_p95_min:.2f} min")
        print(f"    QA-03 (0 perdidos)     : {'✓ CUMPLE' if r.cumple_qa03 else '✗ VIOLA'}")
        print(f"    Tiempo ≤ {MAX_ESPERA_MIN:.0f} min         : {'✓ CUMPLE' if r.cumple_tiempo else '✗ VIOLA'}")

    # ── Tabla comparativa final ────────────────────────────────────────────
    print(f"\n{'═'*65}")
    print("  TABLA COMPARATIVA — ANTES vs. DESPUÉS")
    print(f"{'─'*65}")
    hdr = f"  {'Estrategia':<35} {'Perdidos':>8} {'p95 [min]':>10} {'QA-03':>7}"
    print(hdr)
    print(f"  {'─'*35} {'─'*8} {'─'*10} {'─'*7}")
    for r in resultados:
        cumple = "✓" if r.cumple_qa03 else "✗"
        print(f"  {r.strategy:<35} {r.n_perdidos:>8,} {r.tiempo_p95_min:>10.2f} {cumple:>7}")
    print(f"{'═'*65}")

    _generar_grafico(resultados)


def _generar_grafico(resultados: list[ResumenSimulacion]) -> None:
    """Genera gráfico comparativo de las tres estrategias."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("  [AVISO] matplotlib no disponible — omitiendo gráfico.")
        return

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle(
        "Disponibilidad [QA-03] — San Camilo en Línea 2.0\n"
        f"Monte Carlo N={N_PEDIDOS:,} | P(falla)={P_FALLA_PAGO*100:.0f}% | Duración={DURACION_FALLA_MIN:.0f} min",
        fontsize=13, fontweight="bold",
    )

    nombres_cortos = ["A: Sin\nresiliencia", "B: Reintentos\nbackoff", "C: Outbox\nPattern"]
    colores        = ["#D9534F", "#F0AD4E", "#5CB85C"]

    # ── Subgráfico 1: pedidos perdidos ────────────────────────────────────
    ax1 = axes[0]
    perdidos = [r.n_perdidos for r in resultados]
    bars = ax1.bar(nombres_cortos, perdidos, color=colores, alpha=0.85, edgecolor="white", width=0.5)
    ax1.axhline(0, color="#2E7D32", linewidth=2.5, linestyle="--", label="SLA: 0 pedidos perdidos")

    for bar, val in zip(bars, perdidos):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                 f"{val:,}\n({val/N_PEDIDOS*100:.1f}%)",
                 ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax1.set_title("Pedidos perdidos por estrategia", fontsize=11)
    ax1.set_ylabel("Pedidos perdidos")
    ax1.set_ylim(-50, max(perdidos) * 1.35 + 50)
    ax1.legend(fontsize=9)
    ax1.grid(axis="y", alpha=0.3)

    # ── Subgráfico 2: tiempo p95 de procesamiento ─────────────────────────
    ax2 = axes[1]
    tiempos_p95 = [r.tiempo_p95_min for r in resultados]
    bars2 = ax2.bar(nombres_cortos, tiempos_p95, color=colores, alpha=0.85, edgecolor="white", width=0.5)
    ax2.axhline(MAX_ESPERA_MIN, color="#F0AD4E", linewidth=2, linestyle="--",
                label=f"SLA: p95 ≤ {MAX_ESPERA_MIN:.0f} min")

    for bar, val in zip(bars2, tiempos_p95):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                 f"{val:.1f} min", ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax2.set_title("Tiempo de procesamiento p95 [min]", fontsize=11)
    ax2.set_ylabel("Tiempo p95 [min]")
    ax2.set_ylim(0, max(tiempos_p95) * 1.3 + 1)
    ax2.legend(fontsize=9)
    ax2.grid(axis="y", alpha=0.3)

    # Anotación de conclusión
    ax2.text(0.5, 0.05,
             "Outbox Pattern: 0 pedidos perdidos\n"
             f"Confirmación diferida p95 ≤ {resultados[2].tiempo_p95_min:.1f} min (SLA: {MAX_ESPERA_MIN:.0f} min)",
             transform=ax2.transAxes, ha="center", va="bottom", fontsize=9,
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#E8F5E9", edgecolor="#5CB85C"))

    plt.tight_layout()

    import os
    out_dir  = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "disponibilidad_resultados.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  Gráfico guardado en: {out_path}")


if __name__ == "__main__":
    main()

