"""
San Camilo en Línea — Módulo Pedidos
Esqueleto generado con asistencia de IA (E6 - Round-trip)
Módulo: pedidos
Entidad principal: PedidoGlobal, PedidoPuesto, ItemPedido
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Protocol


# ─────────────────────────────────────────
# Enumeración de estados (E3 — Máquina de Estados)
# ─────────────────────────────────────────

class EstadoPedidoPuesto(Enum):
    """Ciclo de vida de un PedidoPuesto según la máquina de estados E3."""
    RECIBIDO = "RECIBIDO"
    LISTO = "LISTO"
    RECOGIDO = "RECOGIDO"
    ENTREGADO = "ENTREGADO"
    RECHAZADO = "RECHAZADO"


# ─────────────────────────────────────────
# Entidades de dominio
# ─────────────────────────────────────────

@dataclass
class Producto:
    """Producto ofrecido por un Puesto del mercado."""
    id: uuid.UUID
    nombre: str
    precio_unitario: Decimal
    stock_disponible: int

    def reservar_stock(self, cantidad: int) -> None:
        """Reserva unidades del producto para un pedido.

        Args:
            cantidad: número de unidades a reservar.

        Raises:
            ValueError: si no hay suficiente stock disponible.
        """
        if cantidad > self.stock_disponible:
            raise ValueError(
                f"Stock insuficiente para '{self.nombre}': "
                f"solicitado={cantidad}, disponible={self.stock_disponible}"
            )
        self.stock_disponible -= cantidad

    def liberar_stock(self, cantidad: int) -> None:
        """Libera unidades previamente reservadas.

        Args:
            cantidad: número de unidades a liberar.
        """
        self.stock_disponible += cantidad


@dataclass
class Puesto:
    """Puesto comercial dentro del Mercado San Camilo."""
    id: uuid.UUID
    numero_puesto: str
    nombre_comerciante: str
    celular_whatsapp: str


@dataclass
class Cliente:
    """Cliente que realiza pedidos en la plataforma."""
    id: uuid.UUID
    nombre: str
    celular: str
    direccion_delivery: Optional[str] = None


@dataclass
class ItemPedido:
    """Ítem individual dentro de un PedidoPuesto."""
    producto: Producto
    cantidad: int
    precio_unitario: Decimal

    def calcular_subtotal(self) -> Decimal:
        """Retorna el subtotal de este ítem (cantidad × precio unitario)."""
        return self.cantidad * self.precio_unitario


@dataclass
class Pago:
    """Registro de un pago referenciado via Yape."""
    id: uuid.UUID
    monto: Decimal
    codigo_referencia_yape: str
    aprobado: bool = False


@dataclass
class PedidoPuesto:
    """Subpedido dirigido a un único puesto comercial."""
    id: uuid.UUID
    puesto: Puesto
    items: List[ItemPedido] = field(default_factory=list)
    estado: EstadoPedidoPuesto = EstadoPedidoPuesto.RECIBIDO

    # Transiciones de estado válidas según máquina de estados (E3)
    _TRANSICIONES_VALIDAS = {
        EstadoPedidoPuesto.RECIBIDO: {EstadoPedidoPuesto.LISTO, EstadoPedidoPuesto.RECHAZADO},
        EstadoPedidoPuesto.LISTO: {EstadoPedidoPuesto.RECOGIDO, EstadoPedidoPuesto.RECHAZADO},
        EstadoPedidoPuesto.RECOGIDO: {EstadoPedidoPuesto.ENTREGADO},
        EstadoPedidoPuesto.ENTREGADO: set(),
        EstadoPedidoPuesto.RECHAZADO: set(),
    }

    def agregar_item(self, producto: Producto, cantidad: int) -> None:
        """Agrega un ítem al pedido reservando el stock correspondiente."""
        producto.reservar_stock(cantidad)
        self.items.append(
            ItemPedido(
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio_unitario,
            )
        )

    def calcular_subtotal(self) -> Decimal:
        """Suma los subtotales de todos los ítems del pedido."""
        return sum(item.calcular_subtotal() for item in self.items)

    def cambiar_estado(self, nuevo_estado: EstadoPedidoPuesto) -> None:
        """Aplica una transición de estado validada por la máquina de estados.

        Args:
            nuevo_estado: estado destino de la transición.

        Raises:
            ValueError: si la transición no es válida desde el estado actual.
        """
        permitidos = self._TRANSICIONES_VALIDAS.get(self.estado, set())
        if nuevo_estado not in permitidos:
            raise ValueError(
                f"Transición inválida: {self.estado.value} → {nuevo_estado.value}. "
                f"Transiciones permitidas: {[e.value for e in permitidos]}"
            )
        self.estado = nuevo_estado


@dataclass
class PedidoGlobal:
    """Pedido consolidado de un cliente que puede abarcar varios puestos."""
    id: uuid.UUID
    cliente: Cliente
    fecha_creacion: datetime = field(default_factory=datetime.now)
    pedidos_puesto: List[PedidoPuesto] = field(default_factory=list)
    pago: Optional[Pago] = None

    def calcular_monto_total(self) -> Decimal:
        """Suma los subtotales de todos los pedidos por puesto."""
        return sum(pp.calcular_subtotal() for pp in self.pedidos_puesto)

    def confirmar(self) -> None:
        """Confirma el pedido global (requiere pago aprobado)."""
        if self.pago is None or not self.pago.aprobado:
            raise ValueError("No se puede confirmar sin un pago aprobado.")

    def cancelar(self, motivo: str) -> None:
        """Cancela el pedido global liberando el stock reservado en cada ítem."""
        for pp in self.pedidos_puesto:
            for item in pp.items:
                item.producto.liberar_stock(item.cantidad)
            pp.estado = EstadoPedidoPuesto.RECHAZADO


# ─────────────────────────────────────────
# Puertos (interfaces)
# ─────────────────────────────────────────

class PasarelaPago(Protocol):
    """Puerto de salida para verificación de pagos externos."""

    def verificar_pago(self, monto: Decimal, referencia: str) -> Pago:
        """Verifica un pago y retorna un objeto Pago con el resultado."""
        ...


class RepositorioPedidos(Protocol):
    """Puerto de salida para la persistencia de pedidos globales."""

    def guardar(self, pedido: PedidoGlobal) -> None:
        """Persiste el pedido global en el almacenamiento."""
        ...

    def buscar_por_id(self, pedido_id: uuid.UUID) -> Optional[PedidoGlobal]:
        """Recupera un pedido global por su identificador."""
        ...


class NotificadorWhatsApp(Protocol):
    """Puerto de salida para el envío de notificaciones por WhatsApp."""

    def notificar_nuevo_pedido_comerciante(
        self, puesto: Puesto, pedido_puesto: PedidoPuesto
    ) -> None:
        """Envía una notificación WhatsApp al comerciante del puesto."""
        ...


# ─────────────────────────────────────────
# Servicio de aplicación
# ─────────────────────────────────────────

class ServicioPedidos:
    """Servicio de aplicación que orquesta el flujo de creación de pedidos.

    Depende únicamente de puertos (interfaces), nunca de implementaciones
    concretas de infraestructura (Principio de Inversión de Dependencias).
    """

    def __init__(
        self,
        repositorio: RepositorioPedidos,
        pasarela: PasarelaPago,
        notificador: NotificadorWhatsApp,
    ) -> None:
        self._repositorio = repositorio
        self._pasarela = pasarela
        self._notificador = notificador

    def crear_pedido_multi_puesto(
        self,
        cliente: Cliente,
        items_por_puesto: List[tuple[Puesto, List[tuple[Producto, int]]]],
    ) -> PedidoGlobal:
        """Crea un PedidoGlobal con subpedidos por puesto.

        Args:
            cliente: cliente que realiza el pedido.
            items_por_puesto: lista de tuplas (Puesto, [(Producto, cantidad)]).

        Returns:
            PedidoGlobal con todos los PedidoPuesto inicializados.
        """
        pedido = PedidoGlobal(id=uuid.uuid4(), cliente=cliente)
        for puesto, items in items_por_puesto:
            pp = PedidoPuesto(id=uuid.uuid4(), puesto=puesto)
            for producto, cantidad in items:
                pp.agregar_item(producto, cantidad)
            pedido.pedidos_puesto.append(pp)
        self._repositorio.guardar(pedido)
        return pedido

    def procesar_pago_yape(
        self, pedido: PedidoGlobal, referencia: str
    ) -> bool:
        """Verifica el pago Yape y, si es aprobado, notifica a cada comerciante.

        Args:
            pedido: pedido global a pagar.
            referencia: código de referencia Yape.

        Returns:
            True si el pago fue aprobado, False en caso contrario.
        """
        pago = self._pasarela.verificar_pago(pedido.calcular_monto_total(), referencia)
        pedido.pago = pago
        if pago.aprobado:
            pedido.confirmar()
            self._repositorio.guardar(pedido)
            for pp in pedido.pedidos_puesto:
                self._notificador.notificar_nuevo_pedido_comerciante(pp.puesto, pp)
        else:
            pedido.cancelar("Pago rechazado por la pasarela")
            self._repositorio.guardar(pedido)
        return pago.aprobado

