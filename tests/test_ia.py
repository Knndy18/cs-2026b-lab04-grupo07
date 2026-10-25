"""
Tests del componente de IA — San Camilo en Línea
Laboratorio 07 — Entregable E5

Valida los tres patrones de diseño aplicados:
  - Strategy / Adapter: intercambio de proveedores LLM.
  - Decorator (Caché): respuestas cacheadas sin re-invocar al LLM.
  - Chain of Responsibility (Guardrails): bloqueo de entradas/salidas inválidas.

Responsable: Kennedy Chirinos Rojas
"""

import pytest

from pedidos.ia import (
    AdaptadorGemini,
    AdaptadorOpenAI,
    GuardrailContenidoProhibido,
    GuardrailEntradaVacia,
    GuardrailFormatoRespuesta,
    GuardrailLongitudMaxima,
    GuardrailPreciosValidos,
    LLMConCache,
    LLMSimulado,
    ProveedorLLM,
    ResultadoValidacion,
    ServicioIA,
    crear_cadena_guardrails_entrada,
    crear_cadena_guardrails_salida,
    crear_servicio_ia_default,
)


# ═════════════════════════════════════════════════════════════════════
# STRATEGY / ADAPTER — Tests del patrón Strategy
# ═════════════════════════════════════════════════════════════════════

class TestStrategy:
    """Verifica que los proveedores LLM son intercambiables vía Strategy."""

    def test_llm_simulado_devuelve_respuesta_predefinida(
        self, llm_simulado: LLMSimulado
    ) -> None:
        """El LLM simulado retorna la respuesta configurada para la clave."""
        respuesta = llm_simulado.generar_respuesta("¿Qué frutas tienen?")
        assert "manzanas" in respuesta
        assert "S/ 3.50" in respuesta

    def test_llm_simulado_respuesta_por_defecto(
        self, llm_simulado: LLMSimulado
    ) -> None:
        """Cuando no hay clave coincidente, devuelve respuesta por defecto."""
        respuesta = llm_simulado.generar_respuesta("¿Cuál es el clima hoy?")
        assert respuesta == "No tengo información sobre eso."

    def test_llm_simulado_cuenta_invocaciones(
        self, llm_simulado: LLMSimulado
    ) -> None:
        """El contador de invocaciones se incrementa correctamente."""
        assert llm_simulado.invocaciones == 0
        llm_simulado.generar_respuesta("frutas")
        llm_simulado.generar_respuesta("verduras")
        assert llm_simulado.invocaciones == 2

    def test_proveedores_son_intercambiables(self) -> None:
        """Cualquier proveedor que implemente ProveedorLLM es válido."""
        llm_a = LLMSimulado(respuestas={"hola": "Respuesta A"})
        llm_b = LLMSimulado(respuestas={"hola": "Respuesta B"})

        servicio_a = ServicioIA(proveedor=llm_a)
        servicio_b = ServicioIA(proveedor=llm_b)

        assert servicio_a.consultar("hola").contenido == "Respuesta A"
        assert servicio_b.consultar("hola").contenido == "Respuesta B"

    def test_adaptadores_concretos_heredan_de_proveedor(self) -> None:
        """Los adaptadores concretos son subclases de ProveedorLLM."""
        assert issubclass(AdaptadorOpenAI, ProveedorLLM)
        assert issubclass(AdaptadorGemini, ProveedorLLM)
        assert issubclass(LLMSimulado, ProveedorLLM)

    def test_adaptador_openai_no_implementado(self) -> None:
        """El adaptador OpenAI lanza NotImplementedError sin credenciales."""
        adaptador = AdaptadorOpenAI(api_key="test-key")
        with pytest.raises(NotImplementedError):
            adaptador.generar_respuesta("test")

    def test_adaptador_gemini_no_implementado(self) -> None:
        """El adaptador Gemini lanza NotImplementedError sin credenciales."""
        adaptador = AdaptadorGemini(api_key="test-key")
        with pytest.raises(NotImplementedError):
            adaptador.generar_respuesta("test")


# ═════════════════════════════════════════════════════════════════════
# DECORATOR (CACHÉ) — Tests del patrón Decorator
# ═════════════════════════════════════════════════════════════════════

class TestDecoratorCache:
    """Verifica que el Decorator de caché evita invocaciones repetidas."""

    def test_cache_no_reinvoca_llm_en_consulta_repetida(
        self, llm_simulado: LLMSimulado, llm_con_cache: LLMConCache
    ) -> None:
        """Ante una misma entrada, el LLM subyacente se invoca solo 1 vez."""
        # Primera consulta: se invoca al LLM
        r1 = llm_con_cache.generar_respuesta("¿Qué frutas tienen?")
        assert llm_simulado.invocaciones == 1

        # Segunda consulta idéntica: se sirve de caché
        r2 = llm_con_cache.generar_respuesta("¿Qué frutas tienen?")
        assert llm_simulado.invocaciones == 1  # No se incrementó

        # Las respuestas son idénticas
        assert r1 == r2

    def test_cache_diferencia_consultas_distintas(
        self, llm_simulado: LLMSimulado, llm_con_cache: LLMConCache
    ) -> None:
        """Consultas diferentes sí invocan al LLM subyacente."""
        llm_con_cache.generar_respuesta("frutas")
        llm_con_cache.generar_respuesta("verduras")
        assert llm_simulado.invocaciones == 2

    def test_cache_normaliza_mayusculas_y_espacios(
        self, llm_simulado: LLMSimulado, llm_con_cache: LLMConCache
    ) -> None:
        """El caché normaliza la clave (minúsculas + strip) para mayor hit rate."""
        llm_con_cache.generar_respuesta("  FRUTAS  ")
        llm_con_cache.generar_respuesta("frutas")
        # Solo 1 invocación: la segunda fue hit de caché
        assert llm_simulado.invocaciones == 1

    def test_cache_respeta_capacidad_maxima(self) -> None:
        """El caché no almacena más entradas que la capacidad máxima."""
        llm = LLMSimulado()
        cache = LLMConCache(proveedor=llm, capacidad_maxima=2)

        cache.generar_respuesta("consulta 1")
        cache.generar_respuesta("consulta 2")
        cache.generar_respuesta("consulta 3")  # No se cachea (capacidad = 2)

        assert cache.entradas_en_cache == 2

    def test_limpiar_cache(
        self, llm_simulado: LLMSimulado, llm_con_cache: LLMConCache
    ) -> None:
        """limpiar_cache() vacía el caché y permite re-invocar al LLM."""
        llm_con_cache.generar_respuesta("frutas")
        assert llm_con_cache.entradas_en_cache == 1

        llm_con_cache.limpiar_cache()
        assert llm_con_cache.entradas_en_cache == 0

        # Ahora la misma consulta vuelve a invocar al LLM
        llm_con_cache.generar_respuesta("frutas")
        assert llm_simulado.invocaciones == 2

    def test_decorator_es_transparente_como_proveedor(
        self, llm_con_cache: LLMConCache
    ) -> None:
        """El LLMConCache es un ProveedorLLM válido (transparencia del Decorator)."""
        assert isinstance(llm_con_cache, ProveedorLLM)


# ═════════════════════════════════════════════════════════════════════
# CHAIN OF RESPONSIBILITY (GUARDRAILS) — Tests de la cadena
# ═════════════════════════════════════════════════════════════════════

class TestGuardrailsEntrada:
    """Verifica que los guardrails de entrada bloquean consultas inválidas."""

    def test_bloquea_entrada_vacia(self, servicio_ia_completo: ServicioIA) -> None:
        """Una entrada vacía es rechazada por GuardrailEntradaVacía."""
        resultado = servicio_ia_completo.consultar("")
        assert not resultado.exito
        assert "vacía" in resultado.contenido.lower()

    def test_bloquea_solo_espacios(self, servicio_ia_completo: ServicioIA) -> None:
        """Una entrada de solo espacios es rechazada."""
        resultado = servicio_ia_completo.consultar("    ")
        assert not resultado.exito

    def test_bloquea_entrada_demasiado_larga(
        self, servicio_ia_completo: ServicioIA
    ) -> None:
        """Una entrada que excede la longitud máxima es rechazada."""
        texto_largo = "a" * 2001
        resultado = servicio_ia_completo.consultar(texto_largo)
        assert not resultado.exito
        assert "excede" in resultado.contenido.lower() or "límite" in resultado.contenido.lower()

    def test_bloquea_inyeccion_sql(self, servicio_ia_completo: ServicioIA) -> None:
        """Un intento de inyección SQL es rechazado por contenido prohibido."""
        resultado = servicio_ia_completo.consultar("DROP TABLE pedidos;")
        assert not resultado.exito
        assert "prohibido" in resultado.contenido.lower()

    def test_bloquea_inyeccion_script(
        self, servicio_ia_completo: ServicioIA
    ) -> None:
        """Un intento de inyección XSS es rechazado."""
        resultado = servicio_ia_completo.consultar("Dame info <script>alert(1)</script>")
        assert not resultado.exito

    def test_entrada_valida_pasa_todos_los_guardrails(
        self, servicio_ia_completo: ServicioIA
    ) -> None:
        """Una entrada válida del dominio pasa todos los guardrails."""
        resultado = servicio_ia_completo.consultar("¿Qué frutas tienen en el puesto 3?")
        assert resultado.exito


class TestGuardrailsSalida:
    """Verifica que los guardrails de salida bloquean respuestas inválidas del LLM."""

    def test_bloquea_respuesta_con_alucinacion(
        self, servicio_ia_completo: ServicioIA
    ) -> None:
        """Una respuesta del LLM con marcadores de alucinación es rechazada."""
        resultado = servicio_ia_completo.consultar("alucinacion")
        assert not resultado.exito
        assert resultado.validacion_salida is not None
        assert "alucinación" in resultado.contenido.lower() or "alucinacion" in resultado.contenido.lower()

    def test_bloquea_respuesta_con_precio_cero(
        self, servicio_ia_completo: ServicioIA
    ) -> None:
        """Una respuesta con precio S/ 0.00 es rechazada por GuardrailPreciosVálidos."""
        resultado = servicio_ia_completo.consultar("precio_cero")
        assert not resultado.exito
        assert "precio" in resultado.contenido.lower() or "inválido" in resultado.contenido.lower()

    def test_bloquea_respuesta_con_precio_negativo(
        self, servicio_ia_completo: ServicioIA
    ) -> None:
        """Una respuesta con precio negativo es rechazada."""
        resultado = servicio_ia_completo.consultar("precio_negativo")
        assert not resultado.exito

    def test_bloquea_respuesta_con_contenido_prohibido(
        self, servicio_ia_completo: ServicioIA
    ) -> None:
        """Una respuesta que filtra credenciales es rechazada."""
        resultado = servicio_ia_completo.consultar("inyeccion")
        assert not resultado.exito

    def test_bloquea_respuesta_demasiado_corta(
        self, servicio_ia_completo: ServicioIA
    ) -> None:
        """Una respuesta demasiado corta (posible error) es rechazada."""
        resultado = servicio_ia_completo.consultar("corta")
        assert not resultado.exito
        assert "corta" in resultado.contenido.lower() or "mínimo" in resultado.contenido.lower()

    def test_bloquea_respuesta_con_script(
        self, servicio_ia_completo: ServicioIA
    ) -> None:
        """Una respuesta que contiene <script> es rechazada."""
        resultado = servicio_ia_completo.consultar("script")
        assert not resultado.exito

    def test_respuesta_valida_pasa_guardrails_salida(
        self, servicio_ia_completo: ServicioIA
    ) -> None:
        """Una respuesta válida del dominio pasa los guardrails de salida."""
        resultado = servicio_ia_completo.consultar("puesto_3")
        assert resultado.exito
        assert "quesos frescos" in resultado.contenido


class TestGuardrailsIndividuales:
    """Tests unitarios de cada guardrail aislado."""

    def test_guardrail_entrada_vacia_acepta_texto(self) -> None:
        g = GuardrailEntradaVacia()
        r = g.validar("texto válido")
        assert r.valido

    def test_guardrail_longitud_maxima_configurable(self) -> None:
        g = GuardrailLongitudMaxima(longitud_maxima=10)
        assert not g.validar("a" * 11).valido
        assert g.validar("a" * 10).valido

    def test_guardrail_contenido_prohibido_personalizable(self) -> None:
        g = GuardrailContenidoProhibido(palabras_prohibidas=["PELIGRO"])
        assert not g.validar("Alerta de PELIGRO").valido
        assert g.validar("Todo bien").valido

    def test_guardrail_formato_respuesta_longitud_minima(self) -> None:
        g = GuardrailFormatoRespuesta(longitud_minima=20)
        assert not g.validar("Muy corta").valido
        assert g.validar("Esta es una respuesta suficientemente larga").valido

    def test_guardrail_precios_validos_acepta_precios_positivos(self) -> None:
        g = GuardrailPreciosValidos()
        r = g.validar("Manzanas a S/ 3.50 el kg")
        assert r.valido

    def test_guardrail_precios_validos_rechaza_precio_cero(self) -> None:
        g = GuardrailPreciosValidos()
        r = g.validar("Oferta: S/ 0.00 por kg")
        assert not r.valido

    def test_encadenamiento_fluido(self) -> None:
        """establecer_siguiente() permite encadenamiento g1 → g2 → g3."""
        g1 = GuardrailEntradaVacia()
        g2 = GuardrailLongitudMaxima(longitud_maxima=50)
        g3 = GuardrailContenidoProhibido()
        g1.establecer_siguiente(g2).establecer_siguiente(g3)

        # Texto válido pasa los 3
        assert g1.validar("Hola, ¿qué productos hay?").valido

        # Texto vacío falla en g1
        assert not g1.validar("").valido

        # Texto largo falla en g2
        assert not g1.validar("a" * 51).valido

        # Texto con SQL injection falla en g3
        assert not g1.validar("DROP TABLE pedidos").valido


# ═════════════════════════════════════════════════════════════════════
# INTEGRACIÓN — Tests del flujo completo con los 3 patrones
# ═════════════════════════════════════════════════════════════════════

class TestIntegracionServicioIA:
    """Tests de integración que verifican los 3 patrones trabajando juntos."""

    def test_flujo_completo_exitoso(self, servicio_ia_completo: ServicioIA) -> None:
        """Consulta válida → guardrails entrada OK → LLM → guardrails salida OK."""
        resultado = servicio_ia_completo.consultar("¿Qué frutas tienen?")
        assert resultado.exito
        assert "manzanas" in resultado.contenido

    def test_cache_integrado_en_flujo_completo(
        self, servicio_ia_completo: ServicioIA, llm_simulado: LLMSimulado
    ) -> None:
        """El caché funciona correctamente dentro del flujo completo."""
        r1 = servicio_ia_completo.consultar("¿Qué frutas tienen?")
        r2 = servicio_ia_completo.consultar("¿Qué frutas tienen?")

        assert r1.exito and r2.exito
        assert r1.contenido == r2.contenido
        assert r2.desde_cache
        # El LLM subyacente fue invocado solo 1 vez
        assert llm_simulado.invocaciones == 1

    def test_guardrail_entrada_bloquea_antes_de_invocar_llm(
        self, servicio_ia_completo: ServicioIA, llm_simulado: LLMSimulado
    ) -> None:
        """Si la entrada es inválida, el LLM no se invoca."""
        resultado = servicio_ia_completo.consultar("")
        assert not resultado.exito
        assert llm_simulado.invocaciones == 0

    def test_fabrica_crear_servicio_ia_default(self) -> None:
        """La fábrica crear_servicio_ia_default() produce un servicio funcional."""
        servicio = crear_servicio_ia_default(
            respuestas_simuladas={"saludo": "Bienvenido al Mercado San Camilo. Tenemos frutas frescas a S/ 3.00."}
        )
        resultado = servicio.consultar("saludo")
        assert resultado.exito
        assert "Mercado San Camilo" in resultado.contenido

    def test_resultado_incluye_metadata_de_validacion(
        self, servicio_ia_completo: ServicioIA
    ) -> None:
        """RespuestaIA incluye los resultados de validación para trazabilidad."""
        resultado = servicio_ia_completo.consultar("alucinacion")
        assert not resultado.exito
        assert resultado.validacion_salida is not None
        assert resultado.validacion_salida.guardrail_origen == "GuardrailFormatoRespuesta"

