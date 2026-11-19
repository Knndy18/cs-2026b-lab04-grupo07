# Reproducir la evaluación de E3 y E4

## Preparación

Desde la raíz del repositorio, con Python 3.10 o posterior y Node.js 22.22 o posterior:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r prompts/requirements-evaluacion.txt
export PROMPTFOO_PYTHON="$PWD/.venv/bin/python"
export PROMPTFOO_DISABLE_TELEMETRY=1
```

## Evaluación

Cada configuración relaciona una sola plantilla con su carpeta de respuestas. Así se evita evaluar una plantilla con las muestras de otra versión por un cruce de proveedores.

```bash
cd prompts/criterios
npx --yes promptfoo@0.126.0 eval -c promptfooconfig.v1.yaml --no-cache -o resultados/v1.json
npx --yes promptfoo@0.126.0 eval -c promptfooconfig.v2.yaml --no-cache -o resultados/v2.json
npx --yes promptfoo@0.126.0 eval -c promptfooconfig.yaml --no-cache -o resultados/v3.json
cd ../normalizacion
npx --yes promptfoo@0.126.0 eval -c promptfooconfig.v1.yaml --no-cache -o resultados/v1.json
npx --yes promptfoo@0.126.0 eval -c promptfooconfig.v2.yaml --no-cache -o resultados/v2.json
npx --yes promptfoo@0.126.0 eval -c promptfooconfig.yaml --no-cache -o resultados/v3.json
cd ../..
python -m pytest tests/test_evaluadores_prompts.py tests/test_generador_criterios.py
python prompts/resumir_resultados.py
```

La v1 de criterios debe terminar con casos reprobados. Ese resultado es la línea base, no un error que se deba ocultar con `|| true`. Si hay errores del proveedor, no deben contarse como fallos normales de calidad.

## Qué significa el porcentaje

Se divide el número de casos que pasan todas sus aserciones entre el total de casos. No es el porcentaje de aserciones individuales. La tabla y la comparación de regresiones se generan desde los reportes de promptfoo.

El proveedor grabado lee archivos. No consulta un modelo ni ejecuta realmente el prompt. Las plantillas se renderizan durante la evaluación, pero cambiar sus instrucciones no modifica automáticamente las respuestas guardadas. Por eso las muestras nuevas no acreditan todavía la mejora experimental exigida por el laboratorio.

La v1 de criterios procede del repositorio de Diego. Las demás respuestas son muestras de referencia generadas durante esta sesión. Los detalles y las huellas de integridad están en `procedencia.json`.
