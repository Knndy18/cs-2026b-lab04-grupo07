"""
generador_criterios.py
San Camilo en Línea — Generador de Criterios de Aceptación con Prompts Versionados
Laboratorio 09 — Entregable E6

Integra la invocación de LLM detrás del puerto ProveedorLLM del Laboratorio 07,
cargando plantillas de prompts versionadas y validando la salida con JSON Schema
(defensa en capas - Capa 3: Validación de salida).

Responsable: Kennedy Chirinos Rojas
"""

from __future__ import annotations

import json
import pathlib
from typing import Any, Optional
from jsonschema import ValidationError, validate

from pedidos.ia import ProveedorLLM

RAIZ_PROYECTO = pathlib.Path(__file__).resolve().parent.parent.parent
RUTA_ESQUEMA_DEFAULT = RAIZ_PROYECTO / "prompts" / "criterios" / "esquema.json"
RUTA_PROMPTS_DEFAULT = RAIZ_PROYECTO / "prompts" / "criterios"


class SalidaInvalida(Exception):
    """La respuesta del LLM no cumple el contrato: se descarta y se registra."""


class ProveedorGrabado(ProveedorLLM):
    """Adaptador de ProveedorLLM que lee respuestas grabadas desde el sistema de archivos.
    
    Permite reproducibilidad determinista en pruebas unitarias y de integración
    sin incurrir en costos ni requerir API keys.
    """

    def __init__(self, directorio_grabaciones: pathlib.Path) -> None:
        self.directorio_grabaciones = directorio_grabaciones
        self._contador_invocaciones: int = 0

    @property
    def invocaciones(self) -> int:
        return self._contador_invocaciones

    def generar_respuesta(self, prompt: str) -> str:
        self._contador_invocaciones += 1
        # Intentar extraer id de historia si está delimitado por <historia id="..."> o similar
        import re
        coincidencia = re.search(r'id=["\']?([A-Za-z0-9_-]+)["\']?', prompt)
        if coincidencia:
            caso_id = coincidencia.group(1)
            archivo = self.directorio_grabaciones / f"{caso_id}.txt"
            if archivo.exists():
                return archivo.read_text(encoding="utf-8")
        
        # Búsqueda por nombre de archivo si coincide con alguna palabra clave
        for f in self.directorio_grabaciones.glob("*.txt"):
            if f.stem.lower() in prompt.lower():
                return f.read_text(encoding="utf-8")

        return "{}"

    def completar(self, prompt: str) -> str:
        return self.generar_respuesta(prompt)


class GeneradorCriterios:
    """Generador de criterios de aceptación estructurados en formato JSON / Gherkin.

    Aplica:
      - Strategy (Lab 07): Interfaz ProveedorLLM desacoplada (Simulado, Grabado o Real).
      - Defensa en Capas (Capa 3): Validación estricta con jsonschema.
      - Versionado: Carga dinámica de plantillas versionadas (v1, v2, v3, v3.1).
    """

    def __init__(
        self,
        proveedor: ProveedorLLM,
        version: str = "v1",
        directorio_prompts: Optional[pathlib.Path] = None,
        ruta_esquema: Optional[pathlib.Path] = None,
    ) -> None:
        self._proveedor = proveedor
        self.version = version
        self._directorio_prompts = directorio_prompts or RUTA_PROMPTS_DEFAULT
        self._ruta_esquema = ruta_esquema or RUTA_ESQUEMA_DEFAULT

        if not self._ruta_esquema.exists():
            raise FileNotFoundError(f"Esquema JSON no encontrado en: {self._ruta_esquema}")
        self._esquema = json.loads(self._ruta_esquema.read_text(encoding="utf-8"))

        archivo_plantilla = self._directorio_prompts / f"{version}.txt"
        if not archivo_plantilla.exists():
            raise FileNotFoundError(
                f"Plantilla de prompt version '{version}' no encontrada en: {archivo_plantilla}"
            )
        self._plantilla = archivo_plantilla.read_text(encoding="utf-8")

    @property
    def plantilla(self) -> str:
        return self._plantilla

    def construir_prompt(self, id_historia: str, historia: str) -> str:
        """Reemplaza los marcadores de posición en la plantilla versionada."""
        return (
            self._plantilla
            .replace("{{id}}", id_historia)
            .replace("{{historia}}", historia)
            .replace("{id}", id_historia)
            .replace("{historia}", historia)
        )

    def generar(self, id_historia: str, historia: str) -> dict[str, Any]:
        """Envía el prompt al LLM y valida la salida contra el JSON Schema.
        
        Raises:
            SalidaInvalida: Si la respuesta no es JSON válido o no cumple el esquema.
        """
        prompt = self.construir_prompt(id_historia, historia)

        # Soporte polimórfico para completar() o generar_respuesta()
        if hasattr(self._proveedor, "completar"):
            texto = self._proveedor.completar(prompt)
        elif hasattr(self._proveedor, "generar_respuesta"):
            texto = self._proveedor.generar_respuesta(prompt)
        else:
            raise TypeError("El proveedor LLM debe implementar 'generar_respuesta' o 'completar'")

        try:
            criterios = json.loads(texto)
            validate(instance=criterios, schema=self._esquema)
        except (json.JSONDecodeError, ValidationError) as e:
            raise SalidaInvalida(f"{self.version}/{id_historia}: {e}") from e

        return criterios
