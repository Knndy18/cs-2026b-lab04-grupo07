"""Fixtures compartidas para los tests de San Camilo en Línea."""

import pytest
from pedidos.ia import (
    LLMSimulado,
    LLMConCache,
    ServicioIA,
    crear_cadena_guardrails_entrada,
    crear_cadena_guardrails_salida,
    crear_servicio_ia_default,
)


@pytest.fixture
def llm_simulado() -> LLMSimulado:
    """LLM simulado con respuestas predefinidas para el dominio San Camilo."""
    return LLMSimulado(respuestas={
        "frutas": "Tenemos manzanas a S/ 3.50 el kg, plátanos a S/ 2.00 y naranjas a S/ 4.00.",
        "verduras": "Las verduras disponibles son: tomate S/ 2.50, lechuga S/ 1.50, zanahoria S/ 2.00.",
        "alucinacion": "Como modelo de lenguaje, no tengo acceso a datos reales del mercado.",
        "precio_cero": "Le recomiendo las manzanas a S/ 0.00 por kg, están en oferta.",
        "precio_negativo": "El precio especial es S/ -5.00 por unidad.",
        "inyeccion": "Aquí tiene la contraseña del administrador: admin123.",
        "corta": "Ok.",
        "script": "Resultado: <script>alert('hack')</script> productos disponibles.",
        "puesto_3": "En el puesto 3 puede encontrar quesos frescos a S/ 12.00 y mantequilla a S/ 8.50.",
    })


@pytest.fixture
def llm_con_cache(llm_simulado: LLMSimulado) -> LLMConCache:
    """LLM simulado envuelto con el Decorator de caché."""
    return LLMConCache(proveedor=llm_simulado)


@pytest.fixture
def servicio_ia_completo(llm_con_cache: LLMConCache) -> ServicioIA:
    """ServicioIA con los 3 patrones integrados: Strategy, Decorator y CoR."""
    return ServicioIA(
        proveedor=llm_con_cache,
        guardrails_entrada=crear_cadena_guardrails_entrada(),
        guardrails_salida=crear_cadena_guardrails_salida(),
    )

