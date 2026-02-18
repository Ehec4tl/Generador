"""
gestor_equipo.py - Eventos relacionados con obtención y mejora de equipo.
Implementa los 4 eventos de equipo (E1-E4) usando las clases base.
"""

import random
from typing import List, Dict, Optional

from modulos.gestor_eventos import (
    Evento, TipoEvento, ResultadoEvento, 
    GestorEventosBase, obtener_indice_atributo,
    recalcular_suma_total, asegurar_no_negativo
)
from modulos.gestor_personajes import IndicesPersonaje


class EventoEquipoSimple(Evento):
    def __init__(self, id_evento, nombre, descripcion, variantes,
                 atributo, bonus_exito, bonus_fracaso=0, probabilidad_exito=0.6):
        super().__init__(id_evento, nombre, descripcion, variantes)
        self.tipo = TipoEvento.EQUIPO
        self.atributo = atributo
        self.bonus_exito = bonus_exito
        self.bonus_fracaso = bonus_fracaso
        self.probabilidad_exito = probabilidad_exito
    
    def calcular_resultado(self, personaje):
        if random.random() < self.probabilidad_exito:
            return ResultadoEvento.EXITO
        return ResultadoEvento.FRACASO
    
    def aplicar_consecuencias(self, personaje, resultado):
        if resultado is None:
            return
        idx = obtener_indice_atributo(self.atributo)
        if resultado == ResultadoEvento.EXITO:
            personaje[idx] += self.bonus_exito
        elif resultado == ResultadoEvento.FRACASO:
            personaje[idx] += self.bonus_fracaso
        asegurar_no_negativo(personaje, idx)
        recalcular_suma_total(personaje)


class EventoEquipoDoble(Evento):
    def __init__(self, id_evento, nombre, descripcion, variantes,
                 attr_principal, attr_secundario, bonus_exito, penalizacion, prob=0.5):
        super().__init__(id_evento, nombre, descripcion, variantes)
        self.tipo = TipoEvento.EQUIPO
        self.atributo_principal = attr_principal
        self.atributo_secundario = attr_secundario
        self.bonus_exito = bonus_exito
        self.penalizacion = penalizacion
        self.probabilidad_exito = prob
    
    def calcular_resultado(self, personaje):
        return ResultadoEvento.EXITO if random.random() < self.probabilidad_exito else ResultadoEvento.FRACASO
    
    def aplicar_consecuencias(self, personaje, resultado):
        if resultado is None or resultado != ResultadoEvento.EXITO:
            return
        idx_pri = obtener_indice_atributo(self.atributo_principal)
        idx_sec = obtener_indice_atributo(self.atributo_secundario)
        personaje[idx_pri] += self.bonus_exito
        personaje[idx_sec] += self.penalizacion
        asegurar_no_negativo(personaje, idx_pri)
        asegurar_no_negativo(personaje, idx_sec)
        recalcular_suma_total(personaje)


class EventoEquipoGlobal(Evento):
    def __init__(self, id_evento, nombre, descripcion, variantes, bonus_exito, prob=0.8):
        super().__init__(id_evento, nombre, descripcion, variantes)
        self.tipo = TipoEvento.EQUIPO
        self.bonus_exito = bonus_exito
        self.probabilidad_exito = prob
    
    def calcular_resultado(self, personaje):
        return ResultadoEvento.EXITO if random.random() < self.probabilidad_exito else ResultadoEvento.FRACASO
    
    def aplicar_consecuencias(self, personaje, resultado):
        if resultado is None or resultado != ResultadoEvento.EXITO:
            return
        for idx in IndicesPersonaje.ATRIBUTOS_ABS:
            personaje[idx] += self.bonus_exito
            asegurar_no_negativo(personaje, idx)
        recalcular_suma_total(personaje)


class GestorEquipo(GestorEventosBase):
    def __init__(self):
        super().__init__()
        self.nombre_gestor = "Equipo"
    
    def _procesar_json(self, data):
        for ev in data.get('eventos', []):
            evento = self._crear_evento(ev)
            if evento:
                self.eventos.append(evento)
    
    def _crear_evento(self, ev):
        id_ = ev.get('id', '')
        if 'aplica_a_todos' in ev and ev['aplica_a_todos']:
            return EventoEquipoGlobal(id_, ev.get('nombre', ''), ev.get('descripcion', ''),
                                      ev.get('variantes', []), ev.get('bonus_exito', 0),
                                      ev.get('probabilidad_exito', 0.8))
        elif 'atributo_principal' in ev:
            return EventoEquipoDoble(id_, ev.get('nombre', ''), ev.get('descripcion', ''),
                                     ev.get('variantes', []), ev.get('atributo_principal', 'F'),
                                     ev.get('atributo_secundario', 'RF'), ev.get('bonus_exito', 5),
                                     ev.get('penalizacion', -2), ev.get('probabilidad_exito', 0.5))
        elif 'atributo' in ev:
            return EventoEquipoSimple(id_, ev.get('nombre', ''), ev.get('descripcion', ''),
                                      ev.get('variantes', []), ev.get('atributo', 'F'),
                                      ev.get('bonus_exito', 5), ev.get('bonus_fracaso', 0),
                                      ev.get('probabilidad_exito', 0.6))
        return None
    
    def obtener_descripcion_completa(self, evento, personaje, resultado):
        var = evento.obtener_variante_aleatoria()
        txt = f"[{evento.id}] {evento.nombre}\n  {var}\n"
        if resultado:
            if resultado == ResultadoEvento.EXITO:
                txt += f"  ✅ Éxito: +{evento.bonus_exito}\n"
            else:
                txt += f"  ❌ Fracaso\n"
        return txt


if __name__ == "__main__":
    print("🧪 Probando GestorEquipo...")
    gestor = GestorEquipo()
    print("✅ Pruebas completadas")