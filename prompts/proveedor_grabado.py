import pathlib

RAIZ_PROMPTS = pathlib.Path(__file__).parent

def call_api(prompt, options, context):
    config = options.get("config", {})
    tarea = config.get("tarea", "criterios")
    version = config.get("version", "v1")
    
    vars_caso = context.get("vars", {})
    caso_id = vars_caso.get("id", "H1")
    
    ruta_grabacion = RAIZ_PROMPTS / tarea / "grabaciones" / version / f"{caso_id}.txt"
    
    if not ruta_grabacion.exists():
        return {
            "error": f"No se encontró la grabación en {ruta_grabacion}"
        }
        
    salida = ruta_grabacion.read_text(encoding="utf-8")
    return {
        "output": salida
    }
