import pytest
from src.pedidos.estados import Borrador, Confirmado, Pagado, Cancelado
from src.pedidos.eventos import PublicadorEventos, NotificadorComerciante, Suscriptor


class PedidoDummy:
    """Doble de prueba para validar el comportamiento del estado de forma aislada."""
    def __init__(self):
        self.estado_obj = Borrador()
        self.lineas = ["Queso Paria 1kg", "Papa Amarilla 2kg"]
        self.operacion = None

    @property
    def estado(self):
        return self.estado_obj.nombre

    def cambiar_a(self, nuevo_estado):
        self.estado_obj = nuevo_estado

    def confirmar(self):
        self.estado_obj.confirmar(self)

    def pagar(self, operacion):
        self.estado_obj.pagar(self, operacion)

    def cancelar(self):
        self.estado_obj.cancelar(self)


def test_state_transicion_valida_completa():
    pedido = PedidoDummy()
    assert pedido.estado == "BORRADOR"
    
    pedido.confirmar()
    assert pedido.estado == "CONFIRMADO"
    
    pedido.pagar("TX-YAPE-9988")
    assert pedido.estado == "PAGADO"
    assert pedido.operacion == "TX-YAPE-9988"


def test_state_impide_transiciones_invalidas():
    pedido = PedidoDummy()
    # Un pedido en BORRADOR no puede pasar directo a PAGADO
    with pytest.raises(ValueError, match="No se puede pagar"):
        pedido.pagar("TX-INVALIDA")
        
    pedido.confirmar()
    pedido.pagar("TX-OK")
    
    # Un pedido PAGADO no puede volver a confirmarse ni cancelarse
    with pytest.raises(ValueError, match="No se puede confirmar"):
        pedido.confirmar()
    with pytest.raises(ValueError, match="No se puede cancelar"):
        pedido.cancelar()


def test_observer_notifica_a_comerciantes_y_permite_extension():
    publicador = PublicadorEventos()
    bandeja_comerciante = []
    bandeja_auditoria = []

    # Suscriptor nuevo creado para demostrar desacoplamiento (Principio OCP)
    class NotificadorAuditoriaMunicipal(Suscriptor):
        def actualizar(self, evento, datos):
            bandeja_auditoria.append(f"auditoria_fiscal:{datos['id']}")

    publicador.suscribir("pedido_pagado", NotificadorComerciante(bandeja_comerciante))
    publicador.suscribir("pedido_pagado", NotificadorAuditoriaMunicipal())

    datos_evento = {"id": 104, "puesto_id": "P-45", "total": 42.50}
    publicador.publicar("pedido_pagado", datos_evento)

    assert bandeja_comerciante == ["comerciante_puesto_P-45: Pedido 104 pagado"]
    assert bandeja_auditoria == ["auditoria_fiscal:104"]
