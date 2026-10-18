# Comparación: Diagrama de Secuencia UML vs. Vista Dinámica C4

## Análisis comparativo (E4 – Lab 06)

| Dimensión | Diagrama de Secuencia UML (Lab 05) | Vista Dinámica C4 (Lab 06) |
|---|---|---|
| **Nivel de detalle** | Máximo: muestra actores, clases de dominio internas (`PedidoGlobal`, `PedidoPuesto`, `Producto`), llamadas a métodos con firma, bloques `alt` y `loop`, y mensajes asíncronos diferenciados (`->>`) | Medio-alto: muestra componentes arquitectónicos y sus interacciones numeradas; abstrae los bloques condicionales y los objetos de dominio |
| **Público objetivo** | Desarrolladores y técnicos que necesitan implementar o depurar el flujo; requiere conocer el modelo de dominio | Arquitectos de software, tech leads y stakeholders con perfil técnico-gerencial que validan la lógica de negocio de alto nivel |
| **Artefactos representados** | Objetos individuales del dominio (clases, enumeraciones, repositorios) e interacciones método-a-método | Componentes del monolito modular y contenedores del sistema; no baja al nivel de clases |
| **Mantenibilidad** | Alta resistencia al cambio: renombrar una clase invalida el diagrama | Alta resiliencia: un cambio interno en un módulo no invalida la vista si los contratos entre componentes se mantienen |
| **Uso principal** | Documentación de diseño detallado, revisiones de código y pruebas de integración | Comunicación de arquitectura, revisiones de sprint y validación de decisiones arquitectónicas (ADR) |

### Conclusión

El diagrama de secuencia UML del Lab 05 ofrece una trazabilidad método-a-método indispensable para el equipo de desarrollo, pero su nivel de detalle lo hace inadecuado para comunicar decisiones arquitectónicas a stakeholders no técnicos. La vista dinámica C4 del Lab 06 sacrifica granularidad a cambio de claridad estructural: permite validar que los componentes del monolito modular interactúan sin acoplamientos cíclicos y que el flujo crítico de pago es coherente con los drivers de disponibilidad (QA-02) y modificabilidad (QA-04), siendo el vehículo ideal para revisiones de arquitectura con el equipo completo.

