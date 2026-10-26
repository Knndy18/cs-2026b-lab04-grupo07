from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoPago:
    aprobado: bool
    operacion: str | None = None


# STRATEGY: Puerto (interfaz común para todos los medios de pago)
class PasarelaPago(ABC):
    @abstractmethod
    def cobrar(self, monto: float, celular: str) -> ResultadoPago:
        pass


# ADAPTER: Traduce el SDK de Yape a la interfaz PasarelaPago
class YapeAdapter(PasarelaPago):
    def __init__(self, sdk):
        self._sdk = sdk

    def cobrar(self, monto: float, celular: str) -> ResultadoPago:
        r = self._sdk.realizar_cobro(celular, monto)
        return ResultadoPago(aprobado=r["ok"], operacion=r.get("operacion"))


# ADAPTER: Traduce el cliente de Plin a la interfaz PasarelaPago
class PlinAdapter(PasarelaPago):
    def __init__(self, cliente):
        self._cliente = cliente

    def cobrar(self, monto: float, celular: str) -> ResultadoPago:
        monto_centimos = int(round(monto * 100))
        codigo, tx = self._cliente.charge(monto_centimos, celular)
        return ResultadoPago(aprobado=(codigo == 200), operacion=tx if codigo == 200 else None)


# FACTORY REGISTRO: Crea la estrategia adecuada sin if/elif
class FabricaPasarelas:
    def __init__(self):
        self._creadores = {}

    def registrar(self, medio: str, creador):
        self._creadores[medio] = creador

    def crear(self, medio: str) -> PasarelaPago:
        if medio not in self._creadores:
            raise ValueError(f"Medio de pago no soportado: {medio}")
        return self._creadores[medio]()
