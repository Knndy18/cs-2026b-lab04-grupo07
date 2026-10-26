from abc import ABC, abstractmethod


class Suscriptor(ABC):
    """Interfaz observadora para los interesados en eventos del mercado."""
    @abstractmethod
    def actualizar(self, evento: str, datos: dict):
        pass


class PublicadorEventos:
    """Sujeto observable: gestiona suscripciones y notificaciones."""
    def __init__(self):
        self._suscriptores = {}

    def suscribir(self, evento: str, suscriptor: Suscriptor):
        self._suscriptores.setdefault(evento, []).append(suscriptor)

    def desuscribir(self, evento: str, suscriptor: Suscriptor):
        if evento in self._suscriptores and suscriptor in self._suscriptores[evento]:
            self._suscriptores[evento].remove(suscriptor)

    def publicar(self, evento: str, datos: dict):
        for s in self._suscriptores.get(evento, []):
            s.actualizar(evento, datos)


class NotificadorComerciante(Suscriptor):
    """Notifica a los comerciantes de los puestos sobre pedidos confirmados/pagados."""
    def __init__(self, bandeja: list):
        self._bandeja = bandeja

    def actualizar(self, evento: str, datos: dict):
        self._bandeja.append(
            f"comerciante_puesto_{datos.get('puesto_id', 'general')}: Pedido {datos['id']} pagado"
        )


class NotificadorLogistica(Suscriptor):
    """Notifica al área de despacho para el delivery desde San Camilo."""
    def __init__(self, bandeja: list):
        self._bandeja = bandeja

    def actualizar(self, evento: str, datos: dict):
        self._bandeja.append(
            f"logistica: Preparar despacho de S/ {datos['total']:.2f} para pedido {datos['id']}"
        )
