from src.pedidos.despues.servicio import ServicioPedidos, Pedido, LineaPedido
from src.pedidos.pagos import PasarelaPago, ResultadoPago


class PagoEfectivoAdapter(PasarelaPago):
    def cobrar(self, monto: float, celular: str) -> ResultadoPago:
        return ResultadoPago(aprobado=True, operacion="EFECTIVO-001")


def test_open_closed_nuevo_medio_sin_modificar_el_servicio():
    servicio = ServicioPedidos()

    # Se registra un nuevo medio de pago dinámicamente
    servicio.fabrica.registrar("EFECTIVO", lambda: PagoEfectivoAdapter())

    pedido = Pedido(10, "959000111", "Cercado", [LineaPedido("Pan", "puesto-1", 2, 1.0)])
    estado = servicio.procesar_pedido_multipuesto(pedido, "EFECTIVO")

    assert estado == "PAGADO"
    assert pedido.operacion == "EFECTIVO-001"
