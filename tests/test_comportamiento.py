import importlib
import pytest
from src.pedidos.externos import YapeSDK


@pytest.fixture(params=["src.pedidos.antes.servicio"])
def m(request):
    return importlib.import_module(request.param)


def crear_pedido_valido(m, distrito="Cercado", precio=10.0, cantidad=2):
    linea1 = m.LineaPedido("Queso Paria", "puesto-101", cantidad, precio)
    linea2 = m.LineaPedido("Mantequilla", "puesto-102", 1, 5.0)
    return m.Pedido(1, "959000111", distrito, [linea1, linea2])


def test_pago_yape_exitoso(m):
    s = m.ServicioPedidos()
    p = crear_pedido_valido(m)
    estado = s.procesar_pedido_multipuesto(p, "YAPE")
    assert estado == "PAGADO"
    assert p.operacion is not None
    assert len(s.eventos) == 2


def test_pago_plin_exitoso(m):
    s = m.ServicioPedidos()
    p = crear_pedido_valido(m)
    estado = s.procesar_pedido_multipuesto(p, "PLIN")
    assert estado == "PAGADO"


def test_pago_monto_excedido_cancela_pedido(m):
    s = m.ServicioPedidos()
    p = crear_pedido_valido(m, precio=300.0, cantidad=2)  # Excede límite de S/ 500
    estado = s.procesar_pedido_multipuesto(p, "YAPE")
    assert estado == "CANCELADO"


def test_reintento_por_timeout_exitoso(m):
    yape = YapeSDK(fallas=2)
    s = m.ServicioPedidos(yape=yape)
    p = crear_pedido_valido(m)
    estado = s.procesar_pedido_multipuesto(p, "YAPE")
    assert estado == "PAGADO"
    assert yape.llamadas == 3


def test_calculo_delivery_segun_distrito_y_puestos(m):
    s = m.ServicioPedidos()
    p = crear_pedido_valido(m, distrito="Cayma")  # Base 8.5 + 1 puesto extra (2.5) = 11.0
    s.procesar_pedido_multipuesto(p, "YAPE")
    # Subtotal 25 + Delivery 11 = 36.00
    assert "S/36.00" in s.eventos[0]


def test_pedido_sin_lineas_lanza_excepcion(m):
    s = m.ServicioPedidos()
    p = m.Pedido(1, "959000111", "Cercado", [])
    with pytest.raises(ValueError, match="no tiene líneas"):
        s.procesar_pedido_multipuesto(p, "YAPE")


def test_pedido_ya_pagado_lanza_excepcion(m):
    s = m.ServicioPedidos()
    p = crear_pedido_valido(m)
    p.estado = "PAGADO"
    with pytest.raises(ValueError, match="ya fue pagado"):
        s.procesar_pedido_multipuesto(p, "YAPE")


def test_medio_no_soportado_lanza_excepcion(m):
    s = m.ServicioPedidos()
    p = crear_pedido_valido(m)
    with pytest.raises(ValueError, match="no soportado"):
        s.procesar_pedido_multipuesto(p, "BITCOIN")
