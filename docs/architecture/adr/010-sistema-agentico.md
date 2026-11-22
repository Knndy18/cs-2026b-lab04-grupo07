# ADR-010: Arquitectura del Sistema Agéntico para Mantenimiento y Corrección de Incidencias

**Estado:** Aceptado  
**Fecha:** 2026-11-21  
**Autores:** Grupo 07 (San Camilo en Línea)  
**Contexto técnico:** Laboratorio 10 — Sistemas agénticos en la construcción de software

---

## 1. Contexto y Problema

En el desarrollo y mantenimiento del monolito modular de **San Camilo en Línea**, las tareas de corrección de defectos (*issues*) requieren explorar múltiples archivos, formular hipótesis sobre el dominio comercial, modificar código fuente y verificar suites de pruebas automatizadas. Un flujo de trabajo fijo (como las cadenas de prompts del Laboratorio 09) resulta rígido para diagnosticar errores cuya ubicación exacta no se conoce de antemano.

Sin embargo, otorgar autonomía irrestricta a un modelo de lenguaje sobre el repositorio introduce riesgos críticos:
1. **Exceso de agencia (OWASP LLM06):** Ejecución de comandos arbitrarios de sistema, acceso fuera del directorio del proyecto o alteración de pruebas unitarias para forzar falsos aprobados.
2. **Inyección indirecta de prompts (OWASP LLM01):** Instrucciones maliciosas ocultas en comentarios de código o descripciones de issues que el modelo lee como datos y obedece como órdenes.
3. **Salidas mal formadas ("JSON frágil") y bucles infinitos:** Decisiones incompletas o iteraciones sin límite que degradan la confiabilidad y el costo operativo.

---

## 2. Decisión Arquitectónica

Se adopta una arquitectura agéntica estructurada como una **máquina de estados finitos determinista** con separación estricta entre razonamiento del modelo, validación de contrato, política de seguridad y supervisión humana (*"El agente propone; el contrato y la política filtran; el humano aprueba"*):

1. **Arquetipo (Planificador-Ejecutor + ReAct):**
   * Un **Planificador** descompone el issue en subobjetivos acotados.
   * Un **Ejecutor** opera mediante el bucle **ReAct** (*Decidiendo $\to$ ValidandoContrato $\to$ EvaluandoPolitica $\to$ EsperandoAprobacion $\to$ Ejecutando $\to$ Observando*), ajustando sus acciones según las observaciones reales del entorno.
   * Las operaciones transaccionales deterministas del negocio (cobros Yape/Plin y notificaciones) permanecen como **flujos de trabajo fijos**, aplicando el principio de usar la opción más simple que resuelva el problema.
2. **Coordinación Multiagente (Por Gestor + Actor-Crítico):**
   * Se coordina un **Planificador (gestor)** sin herramientas de escritura, un **Ejecutor (actor)** con capacidad de edición acotada y un **Revisor (crítico)** con permisos estrictos de solo lectura (`ver_cambios`, `leer_archivo`, `buscar`, `ejecutar_pruebas`, `leer_notas`).
   * El ciclo de revisión opera hasta un máximo de **2 rondas actor-crítico**.
3. **Herramientas y Mínimo Privilegio:**
   * Se expone un catálogo reducido (`listar_archivos`, `leer_archivo`, `buscar`, `mapa_repo`, `editar_archivo`, `ejecutar_pruebas`, `ver_cambios`, `ejecutar_comando`) confinado a un **sandbox** de rutas relativas.
   * Los comandos de sistema se restringen mediante expresiones regulares a una lista blanca (`pytest`, `radon`, `lint-imports`, `git status/diff`).
4. **Memoria Dual (Corto Plazo + Notas):**
   * **Memoria de trabajo:** Historial conversacional de la sesión dentro de la ventana de contexto.
   * **Memoria de notas (`notas.md`):** Herramientas `anotar` y `leer_notas` para registrar hipótesis verificadas y reducir pasos exploratorios.
5. **Límites y Guardrails:**
   * Validación estricta de contrato JSON antes de ejecutar cualquier herramienta.
   * Protección de rutas críticas (`tests/` inmutable).
   * Presupuesto acotado: máximo **15 pasos** para el ejecutor y **8 pasos** para el revisor.
   * Registro completo de auditoría en trazas estructuradas **JSONL** y diagramas de secuencia Mermaid.
6. **Rol Humano y Delegación Progresiva:**
   * El sistema opera inicialmente en la **Etapa 2 (Humano como Revisor)** de nuestra hoja de ruta (`agentes/delegacion.md`): el callback `aprobar_edicion` exige confirmación explícita (`s/n`) por consola antes de escribir cambios en disco, y un integrante del equipo aprueba manualmente el Pull Request final.

---

## 3. Alternativas Descartadas

| Alternativa | Motivo de descarte |
|---|---|
| **Flujo de trabajo fijo (cadenas de prompts)** | Incapaz de adaptarse cuando una prueba falla por causas imprevistas o requiere explorar dependencias entre módulos del monolito. |
| **Agente único sin revisor crítico** | Aunque consume menos tokens (6,120 vs. 14,890 caracteres en Issue #02), en nuestras pruebas empíricas pasó por alto casos de borde críticos como `stock_disponible is None`. |
| **Coordinación democrática (3 revisores votando)** | Triplica el costo y la latencia por ronda sin aportar valor proporcional frente al tamaño actual del repositorio (principio de parsimonia). |
| **Agente totalmente autónomo (Humano Gobernador)** | Prematuro para el nivel de madurez actual: en el Issue #01 el modelo intentó obedecer una inyección indirecta (`curl ... \| sh`), demostrando que aún requiere supervisión humana activa. |

---

## 4. Consecuencias

* **Positivas:**
  * **Seguridad verificable:** Ninguna acción fuera de política o ruta protegida puede ejecutarse, incluso si el LLM es manipulado por comentarios maliciosos en el código fuente.
  * **Observabilidad y reproducibilidad:** El patrón *Strategy* (`ModeloGrabado` / `ModeloInteractivo`) junto con las trazas `.jsonl` permite auditar cada transición de estado y reproducir trayectorias en CI sin depender de claves de API.
  * **Calidad de código:** La separación actor-crítico detecta defectos de robustez antes de llegar a la revisión humana.
* **Negativas / Compromisos asumidos:**
  * **Mayor consumo de contexto y pasos:** El esquema multiagente consume aproximadamente el doble de caracteres de contexto que un agente único (14,890 vs. 6,120 caracteres en el Issue #02).
  * **Fricción operativa inicial:** La aprobación manual por consola (`aprobar_edicion`) detiene la ejecución hasta recibir respuesta humana, compromiso necesario hasta cumplir los umbrales de confianza para avanzar a la Etapa 3.
