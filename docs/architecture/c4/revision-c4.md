# Lista de Revisión Oficial del Modelo C4 - San Camilo en Línea

Evaluación estructurada según la lista de cotejo oficial de `c4model.com` aplicada a las vistas del sistema.

## 1. Criterios Generales
* **Título descriptivo:** Sí, cada vista cuenta con su título y alcance identificado.
* **Leyenda explícita:** Sí, se incluye leyenda con código de colores, formas y estereotipos.
* **Alcance del diagrama:** Sí, se delimita claramente la frontera entre el sistema interno y los actores o sistemas externos.

## 2. Elementos del Modelo
* **Nombre claro:** Cada elemento posee un nombre autoexplicativo (sin ambigüedades).
* **Tipo de elemento:** Se distingue explícitamente entre Persona, Software System, Container y Component.
* **Descripción funcional:** Cada caja explica su rol concreto dentro de la operativa del mercado.
* **Tecnología especificada:** En contenedores y componentes se detallan lenguajes, frameworks y motores de almacenamiento.

## 3. Relaciones
* **Intención en la etiqueta:** Cada flecha contiene un verbo que especifica la acción (ej. "Publica ofertas", "Solicita cobros").
* **Dirección consistente:** La flecha apunta hacia el elemento que presta o recibe el servicio de forma coherente con la acción.
* **Protocolos de comunicación:** Se indica el protocolo técnico de transporte (HTTPS/JSON, SQL/TCP, Redis Protocol) en niveles técnicos (Contenedores, Componentes, Dinámica).

## 4. Auditoría Asistida por IA y Falsos Positivos

| Vista Evaluada | Hallazgo reportado por la IA | Verificación del Equipo | Decisión Técnica |
|---|---|---|---|
| Contexto del Sistema | La IA observó que faltaban los protocolos técnicos (ej. HTTPS) en las flechas entre Cliente/Comerciante y la plataforma. | De acuerdo con el estándar C4 (c4model.com), el Nivel 1 está dirigido tanto a personal técnico como de negocio; las relaciones con personas no deben contener detalles de red internos. | **Falso Positivo:** Se mantiene la relación basada en intención funcional ("Explora puestos y realiza pedidos"). |
| Contenedores | La IA sugirió etiquetar la cola de mensajería como un sistema externo. | Celery/Redis forma parte integral de la arquitectura desplegada del sistema para el procesamiento en segundo plano. | **Corregido por el equipo:** Se mantiene como contenedor interno dentro del límite del sistema. |
| Componentes | La IA detectó una posible dependencia cíclica entre el módulo de Pedidos y Catálogo. | Se verificó que el flujo de reserva es unidireccional, garantizando acoplamiento limpio según paquetes.puml. | **Aclarado:** Cumple con la arquitectura modular definida en el laboratorio anterior. |
