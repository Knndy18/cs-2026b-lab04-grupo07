import pytest
from fitness.rendimiento import simular, con_cache, bd_con_indice
from fitness.disponibilidad import simular as simular_pagos

# QA-01: Rendimiento en hora pico - p95 menor o igual a 2000 ms
PRESUPUESTO_P95_MS = 2000

def test_ff01_rendimiento_carga_pico():
    r = simular(lam=16, workers=4, servicio=con_cache(bd_con_indice))
    assert r["p95"] <= PRESUPUESTO_P95_MS, f"p95={r['p95']:.0f} ms excede el presupuesto maximo"

def test_ff02_cero_pedidos_perdidos_con_circuit_breaker():
    # QA-03 / QA-04: Resiliencia ante fallas de pasarela externa
    r = simular_pagos("breaker")
    assert r["perdidos"] == 0, f"Se registraron {r['perdidos']} pedidos perdidos"

def test_ff03_breaker_reduce_llamadas_a_proveedor_caido():
    res_breaker = simular_pagos("breaker")
    res_reintentos = simular_pagos("reintentos")
    assert res_breaker["llamadas_en_caida"] < (res_reintentos["llamadas_en_caida"] / 4), \
        "El circuit breaker no esta mitigando la sobrecarga al proveedor caido"
