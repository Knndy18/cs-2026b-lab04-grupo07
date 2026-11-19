"""
test_generador_criterios.py
San Camilo en Línea — Pruebas Automatizadas de Integración de Prompts (E6)
Laboratorio 09 — Construcción de Software

Pruebas con pytest para validar:
  1. Aceptación de respuestas válidas conforme al contrato JSON Schema.
  2. Rechazo estricto con SalidaInvalida ante respuestas inválidas o malformadas.
  3. Rechazo ante esquemas violados (tipos erróneos, enums no permitidos, campos faltantes).
  4. Integración con el proveedor grabado de respuestas históricas.

Responsable: Kennedy Chirinos Rojas
"""

import json
import pathlib
import pytest

from pedidos.ia import LLMSimulado, ProveedorLLM
from pedidos.generador_criterios import GeneradorCriterios, ProveedorGrabado, SalidaInvalida

RAIZ_PROYECTO = pathlib.Path(__file__).resolve().parent.parent
RUTA_PROMPTS = RAIZ_PROYECTO / "prompts" / "criterios"
RUTA_ESQUEMA = RUTA_PROMPTS / "esquema.json"
RUTA_GRABACIONES_V1 = RUTA_PROMPTS / "grabaciones" / "v1"


# ─────────────────────────────────────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def respuesta_valida_json() -> str:
    """Respuesta sintética que cumple al 100% con esquema.json."""
    return json.dumps({
        "historia_id": "H1",
        "invest_ok": True,
        "preguntas": [],
        "escenarios": [
            {
                "titulo": "Registro exitoso de producto",
                "tipo": "exito",
                "dado": ["un comerciante autenticado del puesto 104"],
                "cuando": "registra 'Queso Paria' a 28.50 soles por kilo",
                "entonces": ["el producto se visualiza en el catálogo de San Camilo"]
            },
            {
                "titulo": "Precio no numérico o negativo",
                "tipo": "error",
                "dado": ["un comerciante en el formulario de registro"],
                "cuando": "ingresa un precio de -5.00 soles",
                "entonces": ["el sistema muestra 'El precio debe ser mayor a cero'"]
            }
        ]
    })


@pytest.fixture
def respuesta_invalida_no_invest_json() -> str:
    """Respuesta válida para un caso No INVEST (invest_ok=false y preguntas)."""
    return json.dumps({
        "historia_id": "H6",
        "invest_ok": False,
        "preguntas": [
            "¿Qué métrica específica define 'súper rápido' (ej. tiempo de carga en segundos)?",
            "¿Cuáles son los flujos principales que deben priorizarse para adultos mayores?"
        ],
        "escenarios": []
    })


class ProveedorFijo(ProveedorLLM):
    """Proveedor de prueba que siempre devuelve una cadena predeterminada."""
    def __init__(self, texto: str) -> None:
        self.texto = texto
        self.invocaciones = 0

    def generar_respuesta(self, prompt: str) -> str:
        self.invocaciones += 1
        return self.texto


# ─────────────────────────────────────────────────────────────────────────────
# TESTS UNITARIOS Y DE INTEGRACIÓN (E6)
# ─────────────────────────────────────────────────────────────────────────────

class TestGeneradorCriterios:
    """Pruebas del componente GeneradorCriterios detrás de ProveedorLLM."""

    def test_respuesta_valida_es_aceptada_y_retorna_dict(self, respuesta_valida_json: str):
        """Caso 1: Una respuesta que cumple el esquema es aceptada y parseada."""
        proveedor = ProveedorFijo(respuesta_valida_json)
        generador = GeneradorCriterios(
            proveedor=proveedor,
            version="v1",
            directorio_prompts=RUTA_PROMPTS,
            ruta_esquema=RUTA_ESQUEMA,
        )

        resultado = generador.generar("H1", "Como comerciante quiero registrar queso paria...")

        assert isinstance(resultado, dict)
        assert resultado["historia_id"] == "H1"
        assert resultado["invest_ok"] is True
        assert len(resultado["escenarios"]) == 2
        assert resultado["escenarios"][0]["tipo"] == "exito"
        assert resultado["escenarios"][1]["tipo"] == "error"

    def test_respuesta_no_invest_valida_es_aceptada(self, respuesta_invalida_no_invest_json: str):
        """Caso 1b: Una respuesta que rechaza una historia no INVEST según el esquema es aceptada."""
        proveedor = ProveedorFijo(respuesta_invalida_no_invest_json)
        generador = GeneradorCriterios(
            proveedor=proveedor,
            version="v1",
            directorio_prompts=RUTA_PROMPTS,
            ruta_esquema=RUTA_ESQUEMA,
        )

        resultado = generador.generar("H6", "Que la app sea rápida e intuitiva...")

        assert resultado["invest_ok"] is False
        assert len(resultado["preguntas"]) == 2
        assert len(resultado["escenarios"]) == 0

    def test_respuesta_invalida_texto_plano_lanza_salida_invalida(self):
        """Caso 2: Respuesta en texto plano (como la v1 ingenua) es rechazada con SalidaInvalida."""
        texto_plano = (
            "Criterios de aceptación:\n"
            "1. El comerciante ingresa el producto.\n"
            "2. Se guarda en la base de datos."
        )
        proveedor = ProveedorFijo(texto_plano)
        generador = GeneradorCriterios(
            proveedor=proveedor,
            version="v1",
            directorio_prompts=RUTA_PROMPTS,
            ruta_esquema=RUTA_ESQUEMA,
        )

        with pytest.raises(SalidaInvalida) as exc_info:
            generador.generar("H1", "historia...")

        assert "v1/H1" in str(exc_info.value)

    def test_respuesta_json_incompleto_viola_esquema_lanza_salida_invalida(self):
        """Caso 3: JSON sintácticamente correcto pero que incumple esquema.json (falta clave requerida)."""
        json_incompleto = json.dumps({
            "historia_id": "H1",
            "invest_ok": True
            # Falta 'preguntas' y 'escenarios' requeridos por esquema.json
        })
        proveedor = ProveedorFijo(json_incompleto)
        generador = GeneradorCriterios(
            proveedor=proveedor,
            version="v1",
            directorio_prompts=RUTA_PROMPTS,
            ruta_esquema=RUTA_ESQUEMA,
        )

        with pytest.raises(SalidaInvalida) as exc_info:
            generador.generar("H1", "historia...")

        assert "v1/H1" in str(exc_info.value)
        assert "preguntas" in str(exc_info.value) or "escenarios" in str(exc_info.value)

    def test_tipo_de_escenario_no_permitido_lanza_salida_invalida(self):
        """Caso 4: Tipo de escenario fuera del enum ['exito', 'error', 'borde']."""
        json_tipo_invalido = json.dumps({
            "historia_id": "H1",
            "invest_ok": True,
            "preguntas": [],
            "escenarios": [{
                "titulo": "Flujo alterno",
                "tipo": "otro_tipo_invalido",
                "dado": ["inicio"],
                "cuando": "hace click",
                "entonces": ["ocurre algo"]
            }]
        })
        proveedor = ProveedorFijo(json_tipo_invalido)
        generador = GeneradorCriterios(
            proveedor=proveedor,
            version="v1",
            directorio_prompts=RUTA_PROMPTS,
            ruta_esquema=RUTA_ESQUEMA,
        )

        with pytest.raises(SalidaInvalida) as exc_info:
            generador.generar("H1", "historia...")

        assert "otro_tipo_invalido" in str(exc_info.value) or "enum" in str(exc_info.value)

    def test_proveedor_grabado_v1_falla_por_no_cumplir_contrato(self):
        """Caso 5: Las grabaciones reales de v1 (texto plano) son rechazadas por el validador."""
        proveedor_grabado = ProveedorGrabado(directorio_grabaciones=RUTA_GRABACIONES_V1)
        generador = GeneradorCriterios(
            proveedor=proveedor_grabado,
            version="v1",
            directorio_prompts=RUTA_PROMPTS,
            ruta_esquema=RUTA_ESQUEMA,
        )

        # En v1, H1 es texto no estructurado: el validador debe rechazarlo
        with pytest.raises(SalidaInvalida):
            generador.generar("H1", "historia H1")

    def test_construir_prompt_sustituye_variables(self):
        """Verifica que construir_prompt sustituye {{id}} y {{historia}}."""
        proveedor = LLMSimulado()
        generador = GeneradorCriterios(
            proveedor=proveedor,
            version="v1",
            directorio_prompts=RUTA_PROMPTS,
            ruta_esquema=RUTA_ESQUEMA,
        )

        prompt_construido = generador.construir_prompt("H1", "Historia de prueba de quesos")
        assert "Historia de prueba de quesos" in prompt_construido
        assert "{{historia}}" not in prompt_construido
