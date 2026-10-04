# Matriz de decisión – San Camilo en Línea

## Alternativas
- **A. Monolito en capas:** Un solo despliegue con presentación, servicios, dominio y persistencia compartidos. Es muy rápido de implementar inicialmente, pero el acoplamiento directo entre capas facilita que las reglas de negocio de un módulo (como Pedidos o Catalogo) se mezclen, dificultando la modificabilidad y la gestión limpia de integraciones externas.
- **B. Monolito modular:** Un solo despliegue dividido internamente en módulos explícitos (Catalogo, Pedidos, Pagos, Notificaciones y Entregas) con interfaces públicas estrictas. Mantiene la simplicidad operativa de desplegar en un solo VPS de bajo costo (R-03) al tiempo que garantiza el aislamiento de dominio necesario para evolucionar componentes sin afectar al resto (QA-04).
- **C. Microservicios:** Arquitectura distribuida donde cada dominio opera como un servicio desplegable independientemente mediante comunicación de red. Ofrece un alto aislamiento y escalado granular, pero introduce transacciones distribuidas, alta latencia y una complejidad operativa inviable para un equipo reducido en un plazo de 1 mes (R-01, R-02).

## Criterios y pesos (deben sumar 100 %)
| Criterio | Peso | Justificación (driver relacionado) |
|---|---|---|
| Tiempo de entrega y viabilidad del equipo | 25 % | R-01 y R-02: El MVP debe salir a producción en 1 mes desarrollado por un equipo de hasta 3 developers. |
| Mantenibilidad y modificabilidad | 20 % | QA-04: Permitir incorporar un nuevo adaptador de pago en $\le 2$ días-persona con 0 cambios en otros módulos. |
| Tolerancia a fallos e integridad de pedidos | 20 % | QA-02 y R-07: Garantizar la persistencia de pedidos multi-puesto (0 pedidos perdidos) ante fallas temporales de WhatsApp o pagos. |
| Facilidad de uso para comerciantes (Capacidad de interacción) | 20 % | QA-01 y R-04: Sostener un flujo liviano de 3 toques o menos en celulares de gama baja sin cuellos de botella en la arquitectura backend. |
| Costo e infraestructura de despliegue | 15 % | R-03: Operar sobre un único servidor o servicio cloud de bajo costo en el MVP. |

## Matriz (puntaje 1 = muy malo ... 5 = excelente)
| Criterio (peso) | A | B | C |
|---|---|---|---|
| Tiempo de entrega y viabilidad del equipo (25 %) | 5 | 4 | 1 |
| Mantenibilidad y modificabilidad (20 %) | 2 | 4 | 5 |
| Tolerancia a fallos e integridad de pedidos (20 %) | 3 | 4 | 5 |
| Facilidad de uso para comerciantes (20 %) | 4 | 5 | 3 |
| Costo e infraestructura de despliegue (15 %) | 5 | 5 | 2 |
| **Total ponderado** | **3,70** | **4,35** | **3,05** |

Total ponderado = $\sum (\text{peso} \times \text{puntaje})$. 
Ejemplo (B): $0,25 \times 4 + 0,20 \times 4 + 0,20 \times 4 + 0,20 \times 5 + 0,15 \times 5 = 1,00 + 0,80 + 0,80 + 1,00 + 0,75 = 4,35$

## Conclusión
Elegimos **B. Monolito modular** porque satisface de forma óptima las restricciones de un desarrollo acelerado de 1 mes (R-01) con un equipo chico (R-02) y presupuesto acotado (R-03), ofreciendo a la vez la estructura necesaria para garantizar la modificabilidad (QA-04) e integridad de pedidos (QA-02) sin incurrir en los costos y la complejidad operativa de los microservicios. Ver [ADR-001](adr/001-estilo-arquitectonico.md).
