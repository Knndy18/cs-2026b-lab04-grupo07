from src.pedidos.externos import YapeSDK, PlinClient
from src.pedidos.pagos import FabricaPasarelas, YapeAdapter, PlinAdapter


class LineaPedido:
    def __init__(self, producto: str, puesto_id: str, cantidad: int, precio: float):
        self.producto = producto
        self.puesto_id = puesto_id
        self.cantidad = cantidad
        self.precio = precio


class Pedido:
    def __init__(self, id_pedido: int, celular: str, distrito: str, lineas: list[LineaPedido]):
        self.id = id_pedido
        self.celular = celular
        self.distrito = distrito
        self.lineas = lineas
        self.estado = "BORRADOR"
        self.operacion = None

    def puestos_unicos(self) -> set[str]:
        return {linea.puesto_id for linea in self.lineas}


class ServicioPedidos:
    def __init__(self, yape=None, plin=None):
        self.yape = yape or YapeSDK()
        self.plin = plin or PlinClient()
        self.eventos = []

        # Inicialización y registro de la Factory
        self.fabrica = FabricaPasarelas()
        self.fabrica.registrar("YAPE", lambda: YapeAdapter(self.yape))
        self.fabrica.registrar("PLIN", lambda: PlinAdapter(self.plin))

    def procesar_pedido_multipuesto(self, pedido: Pedido, medio_pago: str) -> str:
        # Validaciones de estado
        if pedido.estado != "BORRADOR":
            if pedido.estado == "CANCELADO":
                raise ValueError("El pedido está cancelado")
            elif pedido.estado == "PAGADO":
                raise ValueError("El pedido ya fue pagado")
            else:
                raise ValueError("Estado no válido")

        if not pedido.lineas:
            raise ValueError("El pedido no tiene líneas")

        # Se obtiene la estrategia desde la Factory (Valida el medio ANTES de modificar el estado)
        pasarela = self.fabrica.crear(medio_pago)

        # Cálculo de subtotal por líneas
        subtotal = sum(linea.cantidad * linea.precio for linea in pedido.lineas)

        # Cálculo de tarifa de delivery
        puestos_count = len(pedido.puestos_unicos())
        tarifas = {"Cercado": 5.0, "Yanahuara": 7.0, "Cayma": 8.5}
        tarifa_base = tarifas.get(pedido.distrito, 12.0)
        costo_delivery = tarifa_base + (max(0, puestos_count - 1) * 2.5)
        total = subtotal + costo_delivery

        # Cambiar a confirmado
        pedido.estado = "CONFIRMADO"

        # Cobro delegado a la Strategy (sin condicionales por medio de pago)
        resultado = pasarela.cobrar(total, pedido.celular)

        # Finalización y notificaciones
        if resultado.aprobado:
            pedido.estado = "PAGADO"
            pedido.operacion = resultado.operacion
            self.eventos.append(f"whatsapp: {pedido.celular}: Pedido {pedido.id} pagado por S/{total:.2f}")
            self.eventos.append(f"reporte: {pedido.id}: {total:.2f}")
        else:
            pedido.estado = "CANCELADO"

        return pedido.estado
