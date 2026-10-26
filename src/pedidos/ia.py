"""
San Camilo en Línea — Componente de IA para Asistencia de Pedidos
Laboratorio 07 — Patrones de Diseño (E5)

Patrones aplicados:
  - Strategy / Adapter: Desacoplar proveedores de LLM intercambiables.
  - Decorator (Caché): Evitar consultas repetidas al LLM subyacente.
  - Chain of Responsibility (Guardrails): Validar entradas y salidas del modelo.

Responsable: Kennedy Chirinos Rojas
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────────────────────────────
# 1. STRATEGY / ADAPTER — Interfaz y proveedores de LLM
# ─────────────────────────────────────────────────────────────────────

class ProveedorLLM(ABC):
    """Interfaz Strategy para proveedores de modelos de lenguaje.

    Permite intercambiar el proveedor concreto (OpenAI, Gemini, LLM local,
    o un simulado para pruebas) sin modificar el servicio de IA.
    """

    @abstractmethod
    def generar_respuesta(self, prompt: str) -> str:
        """Envía un prompt al modelo y retorna la respuesta cruda.

        Args:
            prompt: texto de entrada para el modelo.

        Returns:
            Respuesta generada por el modelo como cadena de texto.
        """


class LLMSimulado(ProveedorLLM):
    """Proveedor simulado (Fake/Mock) para pruebas unitarias.

    Devuelve respuestas predefinidas según el contenido del prompt,
    permitiendo simular escenarios de éxito, alucinaciones, respuestas
    malformadas y violaciones de seguridad.
    """

    def __init__(self, respuestas: Optional[dict[str, str]] = None) -> None:
        """Inicializa el LLM simulado con un diccionario de respuestas.

        Args:
            respuestas: mapeo de subcadenas del prompt a respuestas fijas.
                        Si el prompt contiene la clave, devuelve el valor.
        """
        self._respuestas = respuestas or {}
        self._contador_invocaciones: int = 0

    @property
    def invocaciones(self) -> int:
        """Número total de veces que se invocó generar_respuesta."""
        return self._contador_invocaciones

    def generar_respuesta(self, prompt: str) -> str:
        self._contador_invocaciones += 1
        for clave, respuesta in self._respuestas.items():
            if clave.lower() in prompt.lower():
                return respuesta
        return "No tengo información sobre eso."


class AdaptadorOpenAI(ProveedorLLM):
    """Adaptador para la API de OpenAI (estructura de referencia).

    En producción, este adaptador envolvería la llamada HTTP real a la
    API de OpenAI. Aquí se documenta la interfaz sin dependencias externas.
    """

    def __init__(self, api_key: str, modelo: str = "gpt-4o-mini") -> None:
        self._api_key = api_key
        self._modelo = modelo

    def generar_respuesta(self, prompt: str) -> str:
        # En producción: llamada real a openai.ChatCompletion.create(...)
        raise NotImplementedError(
            "AdaptadorOpenAI requiere credenciales y conectividad. "
            "Use LLMSimulado para pruebas."
        )


class AdaptadorGemini(ProveedorLLM):
    """Adaptador para la API de Google Gemini (estructura de referencia).

    En producción, este adaptador envolvería la llamada HTTP real a la
    API de Gemini. Aquí se documenta la interfaz sin dependencias externas.
    """

    def __init__(self, api_key: str, modelo: str = "gemini-2.0-flash") -> None:
        self._api_key = api_key
        self._modelo = modelo

    def generar_respuesta(self, prompt: str) -> str:
        raise NotImplementedError(
            "AdaptadorGemini requiere credenciales y conectividad. "
            "Use LLMSimulado para pruebas."
        )


# ─────────────────────────────────────────────────────────────────────
# 2. DECORATOR (CACHÉ) — Evitar consultas repetidas al LLM
# ─────────────────────────────────────────────────────────────────────

class LLMConCache(ProveedorLLM):
    """Decorator que intercepta consultas repetidas y devuelve respuestas
    en caché sin volver a invocar al proveedor subyacente.

    Implementa el patrón Decorator: envuelve cualquier ProveedorLLM y
    agrega la responsabilidad de caché de forma transparente.
    """

    def __init__(self, proveedor: ProveedorLLM, capacidad_maxima: int = 128) -> None:
        """Inicializa el decorator de caché.

        Args:
            proveedor: proveedor LLM subyacente a decorar.
            capacidad_maxima: número máximo de entradas en caché.
        """
        self._proveedor = proveedor
        self._cache: dict[str, str] = {}
        self._capacidad_maxima = capacidad_maxima

    @property
    def proveedor_interno(self) -> ProveedorLLM:
        """Acceso al proveedor subyacente (útil para inspección en tests)."""
        return self._proveedor

    @property
    def entradas_en_cache(self) -> int:
        """Número de entradas actualmente almacenadas en caché."""
        return len(self._cache)

    def generar_respuesta(self, prompt: str) -> str:
        """Retorna la respuesta desde caché si existe; de lo contrario,
        consulta al proveedor subyacente y almacena el resultado.
        """
        clave = prompt.strip().lower()
        if clave in self._cache:
            return self._cache[clave]

        respuesta = self._proveedor.generar_respuesta(prompt)

        if len(self._cache) < self._capacidad_maxima:
            self._cache[clave] = respuesta

        return respuesta

    def limpiar_cache(self) -> None:
        """Vacía el caché manualmente."""
        self._cache.clear()


# ─────────────────────────────────────────────────────────────────────
# 3. CHAIN OF RESPONSIBILITY (GUARDRAILS) — Validación de E/S
# ─────────────────────────────────────────────────────────────────────

@dataclass
class ResultadoValidacion:
    """Resultado de la validación de un guardrail.

    Attributes:
        valido: True si la validación pasó correctamente.
        mensaje: descripción del resultado o razón de rechazo.
        guardrail_origen: nombre del guardrail que generó el resultado.
    """
    valido: bool
    mensaje: str
    guardrail_origen: str = ""


class Guardrail(ABC):
    """Eslabón base de la cadena de responsabilidad para guardrails.

    Cada guardrail valida un aspecto de la entrada o salida del LLM.
    Si la validación falla, detiene la cadena y retorna el error.
    Si pasa, delega al siguiente eslabón.
    """

    def __init__(self) -> None:
        self._siguiente: Optional[Guardrail] = None

    def establecer_siguiente(self, siguiente: Guardrail) -> Guardrail:
        """Encadena el siguiente guardrail y lo retorna para encadenamiento fluido.

        Args:
            siguiente: próximo guardrail en la cadena.

        Returns:
            El guardrail siguiente (permite encadenamiento: a.set(b).set(c)).
        """
        self._siguiente = siguiente
        return siguiente

    def validar(self, texto: str) -> ResultadoValidacion:
        """Ejecuta la validación propia y, si pasa, delega al siguiente.

        Args:
            texto: texto a validar (puede ser prompt de entrada o respuesta de salida).

        Returns:
            ResultadoValidacion con el veredicto.
        """
        resultado = self._ejecutar_validacion(texto)
        if not resultado.valido:
            return resultado
        if self._siguiente is not None:
            return self._siguiente.validar(texto)
        return resultado

    @abstractmethod
    def _ejecutar_validacion(self, texto: str) -> ResultadoValidacion:
        """Lógica específica de validación de este guardrail."""


class GuardrailEntradaVacia(Guardrail):
    """Rechaza prompts vacíos o que contengan solo espacios en blanco."""

    def _ejecutar_validacion(self, texto: str) -> ResultadoValidacion:
        if not texto or not texto.strip():
            return ResultadoValidacion(
                valido=False,
                mensaje="La consulta no puede estar vacía.",
                guardrail_origen="GuardrailEntradaVacia",
            )
        return ResultadoValidacion(
            valido=True,
            mensaje="Entrada no vacía.",
            guardrail_origen="GuardrailEntradaVacia",
        )


class GuardrailLongitudMaxima(Guardrail):
    """Rechaza textos que excedan una longitud máxima configurable."""

    def __init__(self, longitud_maxima: int = 2000) -> None:
        super().__init__()
        self._longitud_maxima = longitud_maxima

    def _ejecutar_validacion(self, texto: str) -> ResultadoValidacion:
        if len(texto) > self._longitud_maxima:
            return ResultadoValidacion(
                valido=False,
                mensaje=(
                    f"El texto excede el límite de {self._longitud_maxima} caracteres "
                    f"(tiene {len(texto)})."
                ),
                guardrail_origen="GuardrailLongitudMaxima",
            )
        return ResultadoValidacion(
            valido=True,
            mensaje="Longitud dentro del límite.",
            guardrail_origen="GuardrailLongitudMaxima",
        )


class GuardrailContenidoProhibido(Guardrail):
    """Rechaza textos que contengan palabras o frases prohibidas.

    Útil para filtrar contenido inapropiado, datos sensibles o
    instrucciones de inyección de prompts.
    """

    PALABRAS_PROHIBIDAS_DEFAULT: list[str] = [
        "contraseña",
        "password",
        "api_key",
        "token_secreto",
        "DROP TABLE",
        "DELETE FROM",
        "<script>",
    ]

    def __init__(self, palabras_prohibidas: Optional[list[str]] = None) -> None:
        super().__init__()
        self._prohibidas = palabras_prohibidas or self.PALABRAS_PROHIBIDAS_DEFAULT

    def _ejecutar_validacion(self, texto: str) -> ResultadoValidacion:
        texto_lower = texto.lower()
        for palabra in self._prohibidas:
            if palabra.lower() in texto_lower:
                return ResultadoValidacion(
                    valido=False,
                    mensaje=f"Contenido prohibido detectado: '{palabra}'.",
                    guardrail_origen="GuardrailContenidoProhibido",
                )
        return ResultadoValidacion(
            valido=True,
            mensaje="Sin contenido prohibido.",
            guardrail_origen="GuardrailContenidoProhibido",
        )


class GuardrailFormatoRespuesta(Guardrail):
    """Valida que la respuesta del LLM tenga un formato aceptable.

    Rechaza respuestas vacías, demasiado cortas (posible error) o que
    contengan marcadores de alucinación conocidos.
    """

    MARCADORES_ALUCINACION: list[str] = [
        "como modelo de lenguaje",
        "no tengo acceso a datos reales",
        "no puedo verificar",
        "invento",
        "esto es ficticio",
    ]

    def __init__(self, longitud_minima: int = 10) -> None:
        super().__init__()
        self._longitud_minima = longitud_minima

    def _ejecutar_validacion(self, texto: str) -> ResultadoValidacion:
        if len(texto.strip()) < self._longitud_minima:
            return ResultadoValidacion(
                valido=False,
                mensaje=(
                    f"Respuesta demasiado corta ({len(texto.strip())} caracteres). "
                    f"Mínimo esperado: {self._longitud_minima}."
                ),
                guardrail_origen="GuardrailFormatoRespuesta",
            )
        texto_lower = texto.lower()
        for marcador in self.MARCADORES_ALUCINACION:
            if marcador in texto_lower:
                return ResultadoValidacion(
                    valido=False,
                    mensaje=f"Posible alucinación detectada: '{marcador}'.",
                    guardrail_origen="GuardrailFormatoRespuesta",
                )
        return ResultadoValidacion(
            valido=True,
            mensaje="Formato de respuesta aceptable.",
            guardrail_origen="GuardrailFormatoRespuesta",
        )


class GuardrailPreciosValidos(Guardrail):
    """Valida que la respuesta no mencione precios negativos o cero.

    Guardrail específico del dominio San Camilo: las sugerencias de
    productos no deben contener precios inválidos.
    """

    def _ejecutar_validacion(self, texto: str) -> ResultadoValidacion:
        import re
        # Busca patrones como "S/ 0.00", "S/0", "S/ -5.00", "precio: 0"
        patron_precio_invalido = r"S/\s*-?\d*\.?\d*\b"
        coincidencias = re.findall(patron_precio_invalido, texto)
        for coincidencia in coincidencias:
            # Extraer el valor numérico
            valor_str = coincidencia.replace("S/", "").strip()
            try:
                valor = float(valor_str) if valor_str else -1.0
                if valor <= 0:
                    return ResultadoValidacion(
                        valido=False,
                        mensaje=f"Precio inválido detectado: '{coincidencia}'.",
                        guardrail_origen="GuardrailPreciosValidos",
                    )
            except ValueError:
                continue
        return ResultadoValidacion(
            valido=True,
            mensaje="Precios válidos o sin precios mencionados.",
            guardrail_origen="GuardrailPreciosValidos",
        )


# ─────────────────────────────────────────────────────────────────────
# 4. SERVICIO DE IA — Orquestador que integra los 3 patrones
# ─────────────────────────────────────────────────────────────────────

@dataclass
class RespuestaIA:
    """Respuesta procesada del componente de IA.

    Attributes:
        exito: True si la consulta se procesó correctamente.
        contenido: texto de la respuesta (o mensaje de error).
        desde_cache: True si la respuesta provino del caché.
        validacion_entrada: resultado de los guardrails de entrada.
        validacion_salida: resultado de los guardrails de salida.
    """
    exito: bool
    contenido: str
    desde_cache: bool = False
    validacion_entrada: Optional[ResultadoValidacion] = None
    validacion_salida: Optional[ResultadoValidacion] = None


class ServicioIA:
    """Servicio de IA que orquesta los tres patrones de diseño.

    Flujo:
      1. Validar la entrada del usuario con la cadena de guardrails de entrada.
      2. Consultar al proveedor LLM (con caché Decorator intercalado).
      3. Validar la salida del LLM con la cadena de guardrails de salida.
      4. Retornar la respuesta procesada o el error correspondiente.
    """

    def __init__(
        self,
        proveedor: ProveedorLLM,
        guardrails_entrada: Optional[Guardrail] = None,
        guardrails_salida: Optional[Guardrail] = None,
    ) -> None:
        """Inicializa el servicio de IA.

        Args:
            proveedor: proveedor LLM (puede estar decorado con caché).
            guardrails_entrada: primer eslabón de la cadena de validación
                                de la entrada del usuario.
            guardrails_salida: primer eslabón de la cadena de validación
                               de la respuesta del LLM.
        """
        self._proveedor = proveedor
        self._guardrails_entrada = guardrails_entrada
        self._guardrails_salida = guardrails_salida

    def consultar(self, prompt: str) -> RespuestaIA:
        """Procesa una consulta al componente de IA aplicando guardrails.

        Args:
            prompt: texto de la consulta del usuario.

        Returns:
            RespuestaIA con el resultado del procesamiento.
        """
        # Paso 1: Validar entrada
        if self._guardrails_entrada is not None:
            validacion_in = self._guardrails_entrada.validar(prompt)
            if not validacion_in.valido:
                return RespuestaIA(
                    exito=False,
                    contenido=validacion_in.mensaje,
                    validacion_entrada=validacion_in,
                )
        else:
            validacion_in = None

        # Paso 2: Detectar si vendrá de caché (inspección pre-consulta)
        desde_cache = False
        if isinstance(self._proveedor, LLMConCache):
            clave = prompt.strip().lower()
            desde_cache = clave in self._proveedor._cache

        # Paso 3: Consultar al LLM (o al caché)
        respuesta_llm = self._proveedor.generar_respuesta(prompt)

        # Actualizar flag de caché post-consulta
        if isinstance(self._proveedor, LLMConCache) and not desde_cache:
            desde_cache = False

        # Paso 4: Validar salida
        if self._guardrails_salida is not None:
            validacion_out = self._guardrails_salida.validar(respuesta_llm)
            if not validacion_out.valido:
                return RespuestaIA(
                    exito=False,
                    contenido=validacion_out.mensaje,
                    desde_cache=desde_cache,
                    validacion_entrada=validacion_in,
                    validacion_salida=validacion_out,
                )
        else:
            validacion_out = None

        # Paso 5: Retornar respuesta exitosa
        return RespuestaIA(
            exito=True,
            contenido=respuesta_llm,
            desde_cache=desde_cache,
            validacion_entrada=validacion_in,
            validacion_salida=validacion_out,
        )


# ─────────────────────────────────────────────────────────────────────
# 5. FUNCIONES DE FÁBRICA — Configuración predeterminada
# ─────────────────────────────────────────────────────────────────────

def crear_cadena_guardrails_entrada() -> Guardrail:
    """Crea la cadena de guardrails predeterminada para validar entradas.

    Cadena: EntradaVacía → LongitudMáxima → ContenidoProhibido
    """
    g1 = GuardrailEntradaVacia()
    g2 = GuardrailLongitudMaxima()
    g3 = GuardrailContenidoProhibido()
    g1.establecer_siguiente(g2).establecer_siguiente(g3)
    return g1


def crear_cadena_guardrails_salida() -> Guardrail:
    """Crea la cadena de guardrails predeterminada para validar salidas del LLM.

    Cadena: FormatoRespuesta → PreciosVálidos → ContenidoProhibido
    """
    g1 = GuardrailFormatoRespuesta()
    g2 = GuardrailPreciosValidos()
    g3 = GuardrailContenidoProhibido()
    g1.establecer_siguiente(g2).establecer_siguiente(g3)
    return g1


def crear_servicio_ia_default(
    respuestas_simuladas: Optional[dict[str, str]] = None,
) -> ServicioIA:
    """Crea un ServicioIA completamente configurado con LLM simulado,
    caché y cadenas de guardrails por defecto.

    Ideal para pruebas y desarrollo local.

    Args:
        respuestas_simuladas: mapeo de prompt → respuesta para el LLM simulado.

    Returns:
        ServicioIA configurado y listo para usar.
    """
    llm = LLMSimulado(respuestas=respuestas_simuladas or {})
    llm_con_cache = LLMConCache(proveedor=llm)
    return ServicioIA(
        proveedor=llm_con_cache,
        guardrails_entrada=crear_cadena_guardrails_entrada(),
        guardrails_salida=crear_cadena_guardrails_salida(),
    )

