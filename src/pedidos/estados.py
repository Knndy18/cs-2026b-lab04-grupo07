from abc import ABC, abstractmethod


class EstadoPedido(ABC):
    """Clase base: prohíbe todas las transiciones por defecto."""
    nombre = "DESCONOCIDO"

    def confirmar(self, pedido):
        raise ValueError(f"No se puede confirmar un pedido en estado {self.nombre}")

    def pagar(self, pedido, operacion: str):
        raise ValueError(f"No se puede pagar un pedido en estado {self.nombre}")

    def cancelar(self, pedido):
        raise ValueError(f"No se puede cancelar un pedido en estado {self.nombre}")


class Borrador(EstadoPedido):
    nombre = "BORRADOR"

    def confirmar(self, pedido):
        if not getattr(pedido, "lineas", []):
            raise ValueError("El pedido no tiene líneas")
        pedido.cambiar_a(Confirmado())

    def cancelar(self, pedido):
        pedido.cambiar_a(Cancelado())


class Confirmado(EstadoPedido):
    nombre = "CONFIRMADO"

    def pagar(self, pedido, operacion: str):
        pedido.operacion = operacion
        pedido.cambiar_a(Pagado())

    def cancelar(self, pedido):
        pedido.cambiar_a(Cancelado())


class Pagado(EstadoPedido):
    nombre = "PAGADO"
    # Estado final exitoso: no permite más transiciones


class Cancelado(EstadoPedido):
    nombre = "CANCELADO"
    # Estado final fallido: no permite más transiciones
