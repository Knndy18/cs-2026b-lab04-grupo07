from src.pedidos.externos import YapeSDK, PlinClient


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

        # Cálculo de subtotal por líneas
        subtotal = 0.0
        for linea in pedido.lineas:
            subtotal += linea.cantidad * linea.precio

        # Cálculo de tarifa de delivery (variación según zona y cantidad de puestos)
        puestos_count = len(pedido.puestos_unicos())
        if pedido.distrito == "Cercado":
            tarifa_base = 5.0
        elif pedido.distrito == "Yanahuara":
            tarifa_base = 7.0
        elif pedido.distrito == "Cayma":
            tarifa_base = 8.5
        else:
            tarifa_base = 12.0

        # Recargo por puesto adicional
        costo_delivery = tarifa_base + (max(0, puestos_count - 1) * 2.5)
        total = subtotal + costo_delivery

        # Cambiar a confirmado
        pedido.estado = "CONFIRMADO"
        aprobado, operacion = False, None

        # Bloque if/elif condicional por medio de pago
        if medio_pago == "YAPE":
            for intento in range(3):
                try:
                    r = self.yape.realizar_cobro(pedido.celular, total)
                    aprobado, operacion = r["ok"], r.get("operacion")
                    break
                except TimeoutError:
                    if intento == 2:
                        aprobado = False
        elif medio_pago == "PLIN":
            for intento in range(3):
                try:
                    codigo, tx = self.plin.charge(int(round(total * 100)), pedido.celular)
                    aprobado, operacion = codigo == 200, tx
                    break
                except TimeoutError:
                    if intento == 2:
                        aprobado = False
        else:
            raise ValueError(f"Medio de pago no soportado: {medio_pago}")

        # Finalización y notificaciones
        if aprobado:
            pedido.estado = "PAGADO"
            pedido.operacion = operacion
            self.eventos.append(f"whatsapp: {pedido.celular}: Pedido {pedido.id} pagado por S/{total:.2f}")
            self.eventos.append(f"reporte: {pedido.id}: {total:.2f}")
        else:
            pedido.estado = "CANCELADO"

        return pedido.estado
