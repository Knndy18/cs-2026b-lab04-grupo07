# Drivers arquitectonicos - San Camilo en Linea

## 0. Contexto y proposito

San Camilo en Linea es un MVP para digitalizar la venta de productos de los puestos del Mercado San Camilo. La solucion conecta tres perfiles: clientes que buscan y compran productos, comerciantes que administran su oferta y repartidores que atienden los pedidos con delivery. Tambien debe soportar el recojo en el puesto.

El driver dominante es la **capacidad de interaccion**. El sistema no se dirige unicamente a usuarios acostumbrados a aplicaciones comerciales: algunos comerciantes tendran poca experiencia digital, celulares de gama baja y conectividad movil limitada. Por ello, la arquitectura debe priorizar una interfaz PWA liviana, flujos cortos, formularios simples y persistencia confiable.

Este documento identifica los factores que condicionan la arquitectura. Los identificadores `RF`, `QA` y `R` se reutilizan en los ADR para mantener trazabilidad entre la necesidad, la decision y la verificacion.

## 0.1 Actores y responsabilidades

| Actor | Necesidad principal | Operaciones relevantes |
|---|---|---|
| Cliente | Encontrar productos y completar un pedido confiable. | Consultar catalogo, armar carrito, elegir recojo o delivery y registrar pago. |
| Comerciante | Publicar productos y atender pedidos sin una curva de aprendizaje alta. | Crear productos, cambiar disponibilidad, aceptar pedidos y recibir notificaciones. |
| Repartidor | Conocer que pedidos debe entregar y actualizar su avance. | Consultar asignaciones, cambiar estados y confirmar entrega. |
| Administrador | Mantener la operacion y resolver incidencias. | Gestionar puestos, revisar pedidos, consultar auditoria y administrar cuentas. |
| Servicios externos | Procesar o comunicar una parte del flujo. | Proveedor de pago y servicio de mensajeria WhatsApp. |

## 0.2 Alcance del MVP

El MVP incluira catalogo por puesto, administracion basica de productos, carrito multi-puesto, pedidos para recojo o delivery, registro de pago con Yape, asignacion y seguimiento basico de repartidores, y confirmacion por WhatsApp. No se considera en esta primera version un sistema de contabilidad, optimizacion avanzada de rutas, programa de fidelizacion ni una aplicacion movil nativa.

## 1. Requisitos funcionales clave

| ID | Requisito | Actor | Prioridad |
|---|---|---|---|
| RF-01 | El cliente consulta el catalogo agrupado por puesto del mercado y filtra por nombre, categoria y disponibilidad. | Cliente | Alta |
| RF-02 | El cliente agrega productos de uno o varios puestos al carrito, indicando cantidades y observaciones. | Cliente | Alta |
| RF-03 | El cliente confirma un pedido con modalidad de recojo o delivery, direccion o puesto de recojo y datos de contacto. | Cliente | Alta |
| RF-04 | El cliente registra la constancia o referencia del pago con Yape y el sistema la asocia al pedido. | Cliente | Alta |
| RF-05 | El comerciante publica, edita y desactiva productos desde un celular, con nombre, precio, foto opcional y stock. | Comerciante | Alta |
| RF-06 | El comerciante acepta o rechaza los items correspondientes a su puesto y actualiza su disponibilidad. | Comerciante | Alta |
| RF-07 | El repartidor consulta pedidos asignados y actualiza los estados recogido, en camino y entregado. | Repartidor | Media |
| RF-08 | El sistema confirma el pedido por WhatsApp al comerciante y registra el resultado de la notificacion. | Sistema / Comerciante | Alta |
| RF-09 | El administrador gestiona puestos, usuarios y estados excepcionales de pedidos. | Administrador | Media |

### Criterios de aceptacion funcional

| Requisito | Evidencia esperada |
|---|---|
| RF-01 | Una consulta muestra productos agrupados por puesto y permite aplicar los filtros definidos. |
| RF-02 | El carrito conserva cantidades, puesto de origen y subtotal de cada item antes de confirmar. |
| RF-03 | Un pedido no se confirma sin modalidad, datos de contacto y resumen de items validado. |
| RF-04 | El comprobante o referencia queda asociado al pedido y puede ser revisado por el comerciante. |
| RF-05 | Un comerciante puede publicar un producto y verlo en su propio catalogo sin editar datos de otro puesto. |
| RF-06 | La aceptacion o rechazo cambia el estado del item y queda registrado con fecha y usuario. |
| RF-07 | Cada cambio de estado del delivery conserva actor, fecha y pedido relacionado. |
| RF-08 | El sistema registra enviado, pendiente o fallido y no bloquea la persistencia del pedido por una falla de WhatsApp. |

## 2. Atributos de calidad priorizados

1. **Capacidad de interaccion:** es el atributo critico del caso; el comerciante debe publicar un producto desde un celular de gama baja con pocos pasos y poca experiencia digital.
2. **Disponibilidad y fiabilidad:** los pedidos confirmados no deben perderse aunque WhatsApp o el proveedor de pago presenten una interrupcion temporal.
3. **Rendimiento:** el catalogo, el carrito y la confirmacion de pedidos deben responder dentro de umbrales verificables durante los picos de demanda.
4. **Modificabilidad:** debe ser posible agregar puestos, modalidades de entrega y medios de pago sin modificar todo el sistema.
5. **Seguridad:** las cuentas, pedidos y comprobantes de pago deben estar protegidos contra accesos no autorizados y cambios no auditados.

### Justificacion de prioridad

La capacidad de interaccion ocupa el primer lugar porque una interfaz dificil impediria que los comerciantes mantengan actualizado el catalogo, incluso si el resto del sistema funciona. La disponibilidad ocupa el segundo lugar porque perder un pedido afecta directamente la confianza y puede generar un perjuicio economico. El rendimiento sostiene la experiencia de compra en horas de alta demanda. La modificabilidad reduce el costo de evolucionar el MVP y la seguridad protege la informacion y las operaciones de todos los actores.

## 3. Restricciones

| ID | Tipo | Restriccion |
|---|---|---|
| R-01 | Plazo | El MVP debe estar en produccion en 1 mes; se priorizan funcionalidades esenciales y una arquitectura operable. |
| R-02 | Equipo | Grupo de hasta 3 developers; se priorizan tecnologias ya conocidas por el equipo y responsabilidades simples de operar. |
| R-03 | Presupuesto | Presupuesto bajo; se usara un unico servidor o servicio cloud de bajo costo durante el MVP. |
| R-04 | Dispositivo | Los comerciantes pueden usar celulares de gama baja y conectividad movil limitada; la interfaz no debe depender de hardware moderno. |
| R-05 | Integraciones | El MVP debe contemplar pago con Yape y confirmacion por WhatsApp mediante proveedores o APIs disponibles, sin asumir APIs publicas inexistentes. |
| R-06 | Operacion | Los datos de pedidos deben conservarse y poder auditarse para resolver reclamos de clientes, comerciantes y repartidores. |
| R-07 | Dominio | Un carrito puede contener productos de varios puestos, por lo que el modelo debe conservar la relacion entre pedido, puesto e items. |
| R-08 | Datos | Las credenciales y comprobantes no deben exponerse en logs, prompts ni repositorios publicos. |

## 4. Escenarios de atributos de calidad

| ID | Atributo | Fuente | Estimulo | Entorno | Artefacto | Respuesta | Medida |
|---|---|---|---|---|---|---|---|
| QA-01 | Capacidad de interaccion | Comerciante con poca experiencia digital | Publica un producto con nombre, precio y foto | Celular de gama baja y red 3G | Formulario de productos de la PWA | El sistema guarda el producto y muestra confirmacion | Producto publicado en **3 toques o menos**, en **15 s o menos**, en al menos **90 %** de 20 pruebas |
| QA-02 | Disponibilidad | API de WhatsApp no responde | Se confirma un pedido que requiere notificacion | Operacion normal con servicio externo interrumpido | Modulo de pedidos y cola de notificaciones | El pedido queda persistido y la notificacion se reintenta | **0 pedidos perdidos** en 100 pedidos de prueba y reintento iniciado en **15 min o menos** |
| QA-03 | Rendimiento | 200 clientes concurrentes | Consultan catalogos y agregan productos al carrito | Hora pico de almuerzo, con carga normal de base de datos | API de catalogo y carrito | El sistema devuelve datos y registra el carrito | p95 de lectura del catalogo **<= 2 s** y p95 de agregar al carrito **<= 3 s** |
| QA-04 | Modificabilidad | Product Owner solicita un medio de pago adicional | Se incorpora un nuevo adaptador de pago | Desarrollo sin cambiar reglas de pedidos | Modulo Pagos y puerto de integracion | Se agrega el adaptador sin modificar Catalogo ni Entregas | Cambio implementado en **<= 2 dias-persona** y con **0 cambios** en otros modulos |
| QA-05 | Seguridad | Usuario autenticado intenta acceder a otro puesto | Solicita editar un producto que no le pertenece | Operacion normal | API de productos y autorizacion por rol | El sistema rechaza la operacion y registra el intento | **100 %** de 30 intentos no autorizados rechazados y **0** datos modificados |

## 5. Trazabilidad inicial

| Driver | Decisiones que lo atienden | Evidencia de verificacion |
|---|---|---|
| RF-01, RF-02, RF-03, RF-06, R-07 | ADR-001 y ADR-002 | Modulos Catalogo, Pedidos y Entregas; modelo relacional con pedido, puesto e items. |
| RF-04, RF-08, QA-02, R-05 | ADR-001 y ADR-002 | Adaptadores externos, registro de estados de notificacion y reintentos. |
| RF-05, QA-01, R-04 | ADR-001 y ADR-003 | PWA liviana, flujo corto y autorizacion por puesto. |
| RF-07, QA-05, R-06, R-08 | ADR-002 y ADR-003 | Auditoria de cambios, control de roles y proteccion de credenciales. |
| QA-03, QA-04, R-01, R-02, R-03 | ADR-001 y ADR-002 | Un despliegue, base relacional administrable y separacion de modulos. |

## 6. Estrategia de verificacion

Los escenarios se verificaran mediante pruebas de aceptacion, pruebas de carga y pruebas de autorizacion. QA-01 se evaluara con 20 sesiones observadas en un celular de gama baja; se contabilizaran toques y tiempo desde el formulario vacio hasta la confirmacion. QA-02 se probara desconectando el adaptador de WhatsApp y comparando los pedidos persistidos con las notificaciones reintentadas. QA-03 se medira con una prueba de carga de 200 clientes concurrentes y percentiles p95. QA-04 se verificara incorporando un adaptador simulado y revisando el diff de modulos. QA-05 se ejecutara con una matriz de permisos para los tres roles y evidencia de respuestas HTTP y registros de auditoria.
