# E6 - Round-trip con IA: Modulo `pedidos`

## 1. Proceso de Generacion (Diseno hacia Codigo)

El esqueleto del modulo `pedidos` fue generado con asistencia de IA a partir del diagrama de clases (`clases.puml`) definido en E1. El proceso consistio en:

1. Proporcionar a la IA el diagrama PlantUML `clases.puml` y la maquina de estados `estados-PedidoPuesto.mmd` (E3) como contexto.
2. Solicitar un esqueleto Python idiomatico usando `dataclasses`, `enum` y `typing.Protocol`.
3. Revisar y ajustar el codigo generado para incorporar las restricciones del dominio (validacion de transiciones de estado, reserva de stock).
4. El resultado se guardo en [`src/pedidos/models.py`](../../src/pedidos/models.py).

## 2. Ingenieria Inversa con pyreverse

Se ejecuto el siguiente comando sobre el modulo generado:

```bash
pyreverse -o puml -p pedidos --output-directory docs/design src/pedidos/models.py
```

Esto produjo el archivo [`docs/design/classes_pedidos.puml`](classes_pedidos.puml), que representa el diagrama de clases inferido directamente desde el codigo Python.

## 3. Tabla de Diferencias (Diseno vs. Diagrama Invertido)

| N | Aspecto | Diagrama de diseno (`clases.puml`) | Diagrama invertido (`classes_pedidos.puml`) | Analisis |
|---|---|---|---|---|
| D1 | **Estereotipos y puertos** | Las interfaces usan `<<puerto>>` y `<<adaptador>>` como estereotipos UML. `PasarelaPago`, `RepositorioPedidos` y `NotificadorWhatsApp` estan marcadas explicitamente como interfaces. | pyreverse las genera como clases ordinarias; no distingue `Protocol` de `@dataclass`. Los estereotipos desaparecen. | Los estereotipos son convencion de diseno; Python `Protocol` no produce metadatos que pyreverse pueda leer como interfaz UML. |
| D2 | **Enumeracion `EstadoPedidoPuesto`** | Declarada como bloque `enum { ... }` de PlantUML con todos sus valores listados. | pyreverse la genera como una clase con un unico atributo generico `name`, sin listar los literales de la enumeracion. | pyreverse no extrae los valores de un `Enum` de Python como literales; solo infiere que es una clase. |
| D3 | **Multiplicidades y roles de asociacion** | Las relaciones incluyen multiplicidades explicitas (`1`, `0..*`, `1..*`) y etiquetas de rol (`realiza >`, `contiene >`, `ofrece >`). | pyreverse genera flechas de asociacion sin multiplicidades ni etiquetas. Solo indica el atributo de origen como nombre de flecha. | Las multiplicidades son decisiones de modelado que no pueden inferirse automaticamente del codigo de produccion. |
| D4 | **`ServicioPedidos` y dependencias de uso** | El servicio muestra dependencias de uso (`..>`) hacia `PedidoGlobal`, `RepositorioPedidos`, `PasarelaPago` y `NotificadorWhatsApp`. | pyreverse no genera las dependencias de uso del servicio; solo infiere las referencias directas como campos de instancia. | Las dependencias por inyeccion de constructor no siempre son capturadas por pyreverse si los tipos son `Protocol`. |
| D5 | **`YapeAdapter` y `WhatsAppAdapter`** | El diagrama de diseno incluye los adaptadores concretos `YapeAdapter <<adaptador>>` y la interfaz `NotificadorWhatsApp <<puerto>>`. | El modulo generado no incluye las implementaciones concretas de los adaptadores (pertenecen al paquete `infraestructura`); por tanto, no aparecen en el diagrama invertido. | Es correcto: los adaptadores viven en la capa de infraestructura, fuera del modulo `pedidos`, respetando la separacion de capas de ADR-001. |

## 4. Conclusiones

- El esqueleto generado por IA fue fiel al diagrama de diseno en cuanto a nombres de clases, metodos, atributos y responsabilidades.
- Las principales perdidas en la ingenieria inversa son: estereotipos UML, valores de enumeraciones, multiplicidades y dependencias de uso implicitas.
- Esto confirma que el diagrama de diseno es el artefacto de mayor riqueza semantica; el codigo fuente es su realizacion, no su sustituto.
- La discrepancia D5 evidencia que la arquitectura modular (ADR-001) funciona correctamente: los adaptadores no fugan al dominio.

## 5. Archivos del Round-trip

| Artefacto | Ruta |
|---|---|
| Esqueleto Python (generado con IA) | [`src/pedidos/models.py`](../../src/pedidos/models.py) |
| Diagrama de diseno original | [`docs/design/clases.puml`](clases.puml) |
| Diagrama invertido (pyreverse) | [`docs/design/classes_pedidos.puml`](classes_pedidos.puml) |
