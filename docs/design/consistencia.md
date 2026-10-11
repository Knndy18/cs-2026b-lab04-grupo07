# E7 - Consistencia entre Diagramas UML

## Reglas auditadas (C1-C5)

Las siguientes reglas fueron propuestas por el equipo y verificadas con asistencia de IA sobre los cinco diagramas producidos.

| ID | Regla | Descripcion |
|---|---|---|
| C1 | **Nomenclatura coherente** | Toda entidad presente en el diagrama de clases debe aparecer con el mismo nombre en los demas diagramas donde sea relevante. |
| C2 | **Estados del ciclo de vida** | Los estados usados en el diagrama de secuencia deben ser un subconjunto de los estados definidos en la maquina de estados. |
| C3 | **Cobertura de modulos** | Todos los modulos del ADR-001 deben estar representados en el diagrama de paquetes. |
| C4 | **Sin dependencias ciclicas** | El diagrama de paquetes no debe contener ciclos de dependencia entre modulos de aplicacion. |
| C5 | **Trazabilidad historia-diagrama** | Cada criterio de aceptacion de la historia de usuario debe poder rastrearse a al menos una clase o secuencia en los diagramas. |

---

## Resultados de la auditoria

### C1 - Nomenclatura coherente - Pasa

| Entidad | `clases.puml` | `secuencia-flujo.puml` | `estados-pedido.mmd` | `actividades-preparacion.puml` |
|---|---|---|---|---|
| `PedidoGlobal` | Si | Si | - | Si |
| `PedidoPuesto` | Si | Si | Si | Si |
| `ItemPedido` | Si | Si | - | - |
| `EstadoPedidoPuesto` | Si | - | Si | - |
| `ServicioPedidos` | Si | Si | - | - |

**Resultado:** No se detectaron inconsistencias de nomenclatura entre los diagramas analizados.

---

### C2 - Estados del ciclo de vida - Pasa

Los estados referenciados en el diagrama de secuencia (`RECIBIDO`, `LISTO`, `RECHAZADO`) son subconjunto de los definidos en la maquina de estados (`estados-pedido.mmd`):

```
RECIBIDO -> LISTO -> RECOGIDO -> ENTREGADO
         \-> RECHAZADO
```

**Resultado:** Consistente. El diagrama de secuencia no usa estados no definidos.

---

### C3 - Cobertura de modulos - Pasa

El ADR-001 define cinco modulos de aplicacion: Catalogo, Pedidos, Pagos, Notificaciones y Entregas.

| Modulo | Presente en `paquetes.puml` |
|---|---|
| `catalogo` | Si |
| `pedidos` | Si |
| `pagos` | Si |
| `notificaciones` | Si |
| `entregas` | Si |

**Resultado:** Todos los modulos del ADR-001 estan cubiertos.

---

### C4 - Sin dependencias ciclicas - Pasa

El diagrama de paquetes (`paquetes.puml`) define el siguiente grafo de dependencias:

```
API -> {catalogo, pedidos, pagos, notificaciones, entregas}
pedidos -> {pagos, notificaciones, catalogo}
infraestructura -> {pedidos, catalogo, pagos, notificaciones, entregas}
```

**Analisis de ciclos:** Se verifica que `pagos`, `notificaciones` y `catalogo` no dependen de `pedidos`; `infraestructura` solo depende de puertos (interfaces), no al reves.

**Resultado:** No existen ciclos de dependencia. La regla de dependencia va siempre en direccion `API -> Modulos -> Infraestructura`.

> [!NOTE]
> La dependencia `pedidos -> {pagos, notificaciones}` es unidireccional. `pagos` no conoce a `pedidos`.

---

### C5 - Trazabilidad historia-diagrama - Pasa

| Criterio de aceptacion (historia.md) | Clase/Flujo relacionado |
|---|---|
| CA1: Confirmar pedido multi-puesto con pago Yape aprobado, generar `PedidoPuesto` por comerciante | `ServicioPedidos.procesar_pago_yape()`, `PedidoPuesto`, `Pago` (clases.puml); flujo principal (secuencia) |
| CA1: Cambiar estado a `PAGADO` y notificar por WhatsApp | `EstadoPedidoPuesto` (estados.mmd); `NotificadorWhatsApp` (clases.puml) |
| CA2: Rechazar pedido si pago falla, liberar stock | `PedidoGlobal.cancelar()`, `Producto.liberar_stock()` (clases.puml); rama `[pago rechazado]` (secuencia); estado `RECHAZADO` (estados.mmd) |

**Resultado:** Ambos criterios de aceptacion se trazan a elementos concretos en los diagramas.

---

## Resumen de la auditoria

| Regla | Estado | Observaciones |
|---|---|---|
| C1 - Nomenclatura | Pasa | Nombres uniformes en todos los diagramas |
| C2 - Estados | Pasa | Subconjunto correcto en secuencia |
| C3 - Modulos ADR-001 | Pasa | 5/5 modulos cubiertos |
| C4 - Sin ciclos | Pasa | Grafo aciclico dirigido confirmado |
| C5 - Trazabilidad | Pasa | CA1 y CA2 trazados |

**Conclusion:** Los cinco diagramas son mutuamente consistentes segun las reglas C1-C5.
