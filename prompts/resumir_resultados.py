"""Resume reportes de promptfoo y detecta errores, casos ausentes y regresiones."""
import json
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent


def resumir():
    filas = []
    detalles = {}
    regresiones = []
    for tarea in ("criterios", "normalizacion"):
        esperados = {c["vars"]["id"] for c in yaml.safe_load((RAIZ / tarea / "casos.yaml").read_text())}
        anteriores = None
        for version in ("v1", "v2", "v3"):
            reporte = json.loads((RAIZ / tarea / "resultados" / f"{version}.json").read_text())
            resultados = reporte["results"]["results"]
            por_caso = {}
            for r in resultados:
                caso = r["vars"]["id"]
                if caso in por_caso:
                    raise ValueError(f"Caso duplicado: {tarea}/{version}/{caso}")
                if r.get("response", {}).get("error") or not r.get("gradingResult"):
                    raise ValueError(f"Error del proveedor: {tarea}/{version}/{caso}")
                componentes = r["gradingResult"].get("componentResults", [])
                if not componentes or any("threw error" in c.get("reason", "") for c in componentes):
                    raise ValueError(f"Evaluador incompleto o con error: {tarea}/{version}/{caso}")
                por_caso[caso] = {
                    "aprueba": r["success"],
                    "aserciones_fallidas": [c["assertion"]["metric"] for c in componentes if not c["pass"]],
                }
            if set(por_caso) != esperados:
                raise ValueError(f"Casos distintos del dataset en {tarea}/{version}")
            aprobados = sum(r["aprueba"] for r in por_caso.values())
            filas.append((tarea, version, aprobados, len(esperados), aprobados / len(esperados) * 100))
            detalles[f"{tarea}/{version}"] = por_caso
            if anteriores is not None:
                regresiones.extend(f"{tarea}/{version}/{c}" for c in esperados if anteriores[c]["aprueba"] and not por_caso[c]["aprueba"])
            anteriores = por_caso
    salida = {
        "alcance": "Reproducción de archivos. Las muestras nuevas no son ejecuciones independientes del modelo.",
        "version_promptfoo": "0.126.0",
        "resultados": [dict(tarea=t, version=v, aprobados=a, total=n, porcentaje=p) for t,v,a,n,p in filas],
        "casos": detalles,
        "regresiones_en_archivos": regresiones,
    }
    (RAIZ / "resumen-resultados.json").write_text(json.dumps(salida, ensure_ascii=False, indent=2) + "\n")
    lineas = ["# Resultados de reproducción de archivos", "",
              "Estas tasas describen las respuestas guardadas. Solo v1 de criterios proviene del trabajo previo de Diego. Las demás son muestras de referencia de esta sesión. No acreditan una mejora medida del modelo.", "",
              "| Tarea | Versión | Casos aprobados | Tasa |", "|---|---|---|---|"]
    lineas += [f"| {t} | {v} | {a}/{n} | {p:.2f} % |" for t,v,a,n,p in filas]
    lineas += ["", "Regresiones entre archivos consecutivos: " + (", ".join(regresiones) if regresiones else "ninguna."), "",
               "La ausencia de regresiones en muestras no demuestra ausencia de regresiones del modelo. La normalización reutiliza las mismas respuestas de referencia en sus tres versiones.", "",
               "El detalle por caso y aserción está en `resumen-resultados.json`. Los reportes completos están en las carpetas `resultados` de cada tarea.", ""]
    (RAIZ / "resultados.md").write_text("\n".join(lineas))
    for t,v,a,n,p in filas:
        print(f"{t}/{v}: {a}/{n}, {p:.2f} %")
    if regresiones:
        raise SystemExit("Se detectaron regresiones: " + ", ".join(regresiones))


if __name__ == "__main__":
    resumir()
