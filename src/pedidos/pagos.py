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


# ADAPTER: Traduce el SDK de Yape a la interfaz PasarelaPago con reintentos
class YapeAdapter(PasarelaPago):
    def __init__(self, sdk):
        self._sdk = sdk

    def cobrar(self, monto: float, celular: str) -> ResultadoPago:
        for intento in range(3):
            try:
                r = self._sdk.realizar_cobro(celular, monto)
                return ResultadoPago(aprobado=r["ok"], operacion=r.get("operacion"))
            except TimeoutError:
                if intento == 2:
                    return ResultadoPago(aprobado=False)
        return ResultadoPago(aprobado=False)


# ADAPTER: Traduce el cliente de Plin a la interfaz PasarelaPago con reintentos
class PlinAdapter(PasarelaPago):
    def __init__(self, cliente):
        self._cliente = cliente

    def cobrar(self, monto: float, celular: str) -> ResultadoPago:
        monto_centimos = int(round(monto * 100))
        for intento in range(3):
            try:
                codigo, tx = self._cliente.charge(monto_centimos, celular)
                return ResultadoPago(aprobado=(codigo == 200), operacion=tx if codigo == 200 else None)
            except TimeoutError:
                if intento == 2:
                    return ResultadoPago(aprobado=False)
        return ResultadoPago(aprobado=False)


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
