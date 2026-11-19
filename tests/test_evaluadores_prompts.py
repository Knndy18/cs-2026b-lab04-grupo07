"""Contrapruebas para no confundir una salida bien formada con una correcta."""
import json
from pathlib import Path
import subprocess

import jsonschema
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def cargar(tarea, caso):
    base = ROOT / 'prompts' / tarea
    config = yaml.safe_load((base / 'promptfooconfig.yaml').read_text())
    datos = next(c['vars'] for c in yaml.safe_load((base / 'casos.yaml').read_text()) if c['vars']['id'] == caso)
    salida = json.loads((base / 'grabaciones' / 'v3' / f'{caso}.txt').read_text())
    return base, config, datos, salida


def evaluar(tarea, caso, mutacion=None):
    base, config, datos, salida = cargar(tarea, caso)
    if mutacion:
        mutacion(salida)
    resultados = {}
    for asercion in config['defaultTest']['assert']:
        if asercion['type'] == 'is-json':
            try:
                jsonschema.validate(salida, json.loads((base / 'esquema.json').read_text()))
                resultados[asercion['metric']] = True
            except jsonschema.ValidationError:
                resultados[asercion['metric']] = False
        else:
            script = "const fs=require('node:fs'); const x=JSON.parse(fs.readFileSync(0,'utf8')); const f=new Function('output','context',x.code); process.stdout.write(JSON.stringify(f(x.output,{vars:x.vars})));"
            result = subprocess.run(['node', '-e', script], input=json.dumps({'code': asercion['value'], 'output':json.dumps(salida,ensure_ascii=False),'vars':datos}), text=True, capture_output=True, check=True)
            resultados[asercion['metric']] = json.loads(result.stdout)
    return resultados


def test_no_acepta_rechazar_todas_las_historias():
    r = evaluar('criterios','H1',lambda s:s.update(invest_ok=False,preguntas=['¿Qué se necesita?'],escenarios=[]))
    assert not r['A4_invest_esperado']
    assert not r['A5_identidad_y_necesidad']


def test_no_acepta_copiar_id_de_otro_caso():
    assert not evaluar('criterios','H1',lambda s:s.update(historia_id='H2'))['A5_identidad_y_necesidad']


def test_no_invest_limita_preguntas_a_tres():
    assert not evaluar('criterios','H6',lambda s:s.update(preguntas=['¿Qué tarea?']*4))['A4_invest_esperado']


def test_no_rechaza_reactivar_por_contener_react():
    def cambiar(s): s['escenarios'][0]['cuando'] = 'el comerciante decide reactivar el producto con su precio'
    assert evaluar('criterios','H1',cambiar)['A3_sin_implementacion']
    assert 'react' in 'reactivar'  # El evaluador original sí lo rechazaba.


def test_si_rechaza_tecnologia_en_escenario():
    def cambiar(s): s['escenarios'][0]['entonces'] = ['el producto se guarda en PostgreSQL']
    assert not evaluar('criterios','H1',cambiar)['A3_sin_implementacion']


def test_no_basta_asignar_todo_a_desconocido():
    def cambiar(s): s['resultados'][0].update(producto_id='desconocido',nombre='desconocido')
    r=evaluar('normalizacion','N1',cambiar)
    assert r['B2_catalogo_o_desconocido']
    assert not r['B4_asignacion_esperada']
    assert not r['B5_coincidencia_completa']


def test_no_acepta_id_valido_con_nombre_equivocado():
    def cambiar(s): s['resultados'][0]['nombre']='arroz'
    r=evaluar('normalizacion','N1',cambiar)
    assert not r['B1_contrato_json']
    assert not r['B2_catalogo_o_desconocido']


def test_no_acepta_eliminar_duplicados():
    def cambiar(s): s['resultados'].pop(1)
    assert not evaluar('normalizacion','N8',cambiar)['B3_cantidad_orden_literal']


def test_no_acepta_cambiar_el_texto_original():
    def cambiar(s): s['resultados'][0]['entrada']='queso paria'
    assert not evaluar('normalizacion','N2',cambiar)['B3_cantidad_orden_literal']


def test_no_acepta_extraer_producto_de_una_inyeccion():
    def cambiar(s): s['resultados'][0].update(producto_id='P04',nombre='tomate')
    assert not evaluar('normalizacion','N10',cambiar)['B5_coincidencia_completa']


@pytest.mark.parametrize('caso',['N6','N7','N9','N10'])
def test_bordes_y_adversarios_validos(caso):
    assert all(evaluar('normalizacion',caso).values())
