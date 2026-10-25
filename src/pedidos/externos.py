class YapeSDK:
    def __init__(self, fallas=0):
        self.fallas = fallas
        self.llamadas = 0

    def realizar_cobro(self, telefono: str, soles: float) -> dict:
        self.llamadas += 1
        if self.llamadas <= self.fallas:
            raise TimeoutError("Error de conexion con servidor Yape")
        if soles > 500:
            return {"ok": False, "operacion": None}
        return {"ok": True, "operacion": f"YAPE-{self.llamadas}982"}


class PlinClient:
    def charge(self, amount_cents: int, phone: str) -> tuple[int, str]:
        if amount_cents > 50000:
            return 400, ""
        return 200, f"PLIN-TX-{phone[-4:]}"
