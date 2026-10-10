# Historia de Usuario - HU-02: Pedido a varios puestos con pago único

**Como** Cliente de San Camilo en Línea  
**Quiero** realizar un único pedido que contenga productos de distintos puestos del mercado y pagarlo en una sola transacción con Yape  
**Para** no tener que hacer compras separadas ni múltiples pagos por cada puesto.

## Criterios de Aceptación

### Criterio 1: Confirmación y Pago Exitoso Multi-Puesto
* **Dado** que el cliente tiene un carrito con productos de 2 o más puestos diferentes y stock suficiente en cada oferta.
* **Cuando** el cliente confirma el pedido e ingresa la referencia del pago con Yape por el monto total.
* **Entonces** el sistema registra el pedido global, genera una orden individual (`PedidoPuesto`) para cada comerciante implicado, cambia el estado a `PAGADO` y notifica a cada comerciante por WhatsApp.

### Criterio 2: Rechazo por Falta de Stock o Pago Fallido
* **Dado** que el cliente intenta confirmar un pedido multi-puesto.
* **Cuando** la pasarela de pago rechaza la transacción o uno de los productos seleccionados ya no cuenta con stock disponible.
* **Entonces** el sistema cancela la operación, no genera las órdenes por puesto, libera cualquier reserva temporal de stock y notifica al cliente con el motivo del rechazo.
