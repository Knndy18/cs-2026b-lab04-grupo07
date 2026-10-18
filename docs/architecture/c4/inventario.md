# Inventario de Elementos del Modelo C4 – San Camilo en Línea

| Elemento | Tipo C4 | Descripción / Rol | Origen (Lab 04 / Lab 05) |
|---|---|---|---|
| **Cliente** | Persona | Usuario comprador que navega ofertas, arma su carrito multi-puesto y realiza el pago único. | `drivers.md` (Lab 04) |
| **Comerciante** | Persona | Comerciante del puesto que administra productos, disponibilidad y confirma la preparación del pedido. | `drivers.md` (Lab 04) |
| **Repartidor** | Persona | Personal encargado del recojo en puestos y entrega en el domicilio del cliente. | `drivers.md` (Lab 04) |
| **San Camilo en Línea** | Sistema de software | Plataforma e-commerce MVP que conecta clientes, comerciantes y repartidores para el Mercado San Camilo. | Caso General |
| **Proveedor de Pagos** | Sistema externo (`Externo`) | Pasarela para verificar y procesar las transacciones de pago único con Yape / Plin. | `drivers.md`, `ADR-001` (Lab 04) |
| **WhatsApp Business API** | Sistema externo (`Externo`) | Servicio de mensajería para notificar instantáneamente nuevos pedidos a los comerciantes. | `drivers.md`, `ADR-001` (Lab 04) |
| **Aplicación Web Progresiva (PWA)** | Contenedor | Interfaz web móvil ligera optimizada para celulares de gama baja y red 3G. | `ADR-001` (Lab 04), `clases.puml` (Lab 05) |
| **API Backend** | Contenedor | Monolito modular que implementa la lógica de negocio, catálogo, pedidos y reglas de dominio. | `ADR-001` (Lab 04), `paquetes.puml` (Lab 05) |
| **Base de Datos** | Contenedor (DB) | Base de datos relacional para la persistencia transaccional de pedidos multi-puesto e inventario. | `ADR-002` (Lab 04) |
| **Worker de Tareas** | Contenedor | Procesador asíncrono para reintentos y envío desacoplado de notificaciones por WhatsApp. | `ADR-001` (Lab 04) |
| **Cola y Caché** | Contenedor (Queue) | Broker de mensajería para tareas en segundo plano y caché del catálogo. | `ADR-001` (Lab 04) |
