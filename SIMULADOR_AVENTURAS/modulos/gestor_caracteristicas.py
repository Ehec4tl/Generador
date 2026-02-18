"""
gestor_caracteristicas.py - Eventos de contacto con fuerzas mayores.
Implementa los 8 eventos de características (C1-C8).
Versión corregida con todos los métodos abstractos implementados.
"""

import random
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from modulos.gestor_eventos import (
    Evento, TipoEvento, ResultadoEvento, 
    GestorEventosBase
)
from modulos.gestor_personajes import IndicesPersonaje


# ============================================================================
# CONSTANTES PARA CARACTERÍSTICAS
# ============================================================================

class TiposCaracteristica:
    """Define los tipos de características disponibles."""
    
    # Bendiciones
    BENDICION_VIDA = "Bendición de la Vida"
    BENDICION_DEVORADORES = "Bendición de los Devoradores"
    BENDICION_TRANSFORMACION = "Bendición de la Transformación"
    BENDICION_ANGELICAL = "Bendición Angelical"
    
    # Maldiciones
    MALDICION_NO_MUERTE = "Maldición de la No Muerte"
    MALDICION_DEVORADORES = "Maldición de los Devoradores"
    MALDICION_HIBRIDOS = "Maldición de los Híbridos"
    MALDICION_DEMONIACA = "Maldición Demoníaca"
    
    # Todos los tipos
    TODOS = [
        BENDICION_VIDA, BENDICION_DEVORADORES, BENDICION_TRANSFORMACION, BENDICION_ANGELICAL,
        MALDICION_NO_MUERTE, MALDICION_DEVORADORES, MALDICION_HIBRIDOS, MALDICION_DEMONIACA
    ]


# ============================================================================
# CLASE PARA REGISTRO DE CARACTERÍSTICA
# ============================================================================

class RegistroCaracteristica:
    """
    Almacena una característica adquirida.
    Se guarda en el campo RESERVADO1 del personaje.
    """
    
    def __init__(self, 
                 fuerza: str,
                 es_bendicion: bool,
                 efecto: str,
                 evento_id: str,
                 timestamp: float = None):
        """
        Inicializa un registro de característica.
        
        Args:
            fuerza: Nombre de la fuerza
            es_bendicion: True si es bendición
            efecto: Efecto narrativo
            evento_id: ID del evento que la otorgó
            timestamp: Momento de adquisición
        """
        self.fuerza = fuerza
        self.es_bendicion = es_bendicion
        self.efecto = efecto
        self.evento_id = evento_id
        self.timestamp = timestamp or datetime.now().timestamp()
        self.activo = True
        self.veces_activado = 0
    
    def to_dict(self) -> Dict:
        """Convierte a diccionario para guardar."""
        return {
            "fuerza": self.fuerza,
            "es_bendicion": self.es_bendicion,
            "efecto": self.efecto,
            "evento_id": self.evento_id,
            "timestamp": self.timestamp,
            "activo": self.activo,
            "veces_activado": self.veces_activado
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RegistroCaracteristica':
        """Crea desde diccionario."""
        reg = cls(
            fuerza=data["fuerza"],
            es_bendicion=data["es_bendicion"],
            efecto=data["efecto"],
            evento_id=data["evento_id"],
            timestamp=data["timestamp"]
        )
        reg.activo = data.get("activo", True)
        reg.veces_activado = data.get("veces_activado", 0)
        return reg
    
    def __repr__(self):
        estado = "✅" if self.activo else "❌"
        return f"{estado} {self.fuerza} ({self.efecto})"


# ============================================================================
# EVENTOS DE CARACTERÍSTICA (CORREGIDO)
# ============================================================================

class EventoCaracteristica(Evento):
    """
    Evento de contacto con una fuerza mayor.
    No modifica atributos directamente, sino que añade una "marca"
    que influirá en eventos futuros.
    
    CORREGIDO: Ahora implementa todos los métodos abstractos.
    """
    
    def __init__(self,
                 id_evento: str,
                 nombre: str,
                 descripcion: str,
                 variantes: List[str],
                 fuerza: str,
                 es_bendicion: bool,
                 efecto: str):
        """
        Inicializa un evento de característica.
        
        Args:
            id_evento: Identificador (C1, C2, etc.)
            nombre: Nombre del evento
            descripcion: Descripción base
            variantes: Lista de descripciones alternativas
            fuerza: Nombre de la fuerza (ej: "Bendición de la Vida")
            es_bendicion: True si es bendición, False si es maldición
            efecto: Efecto narrativo
        """
        super().__init__(id_evento, nombre, descripcion, variantes)
        self.tipo = TipoEvento.CARACTERISTICA
        self.fuerza = fuerza
        self.es_bendicion = es_bendicion
        self.efecto = efecto
    
    def calcular_resultado(self, personaje: List) -> Optional[ResultadoEvento]:
        """
        Los eventos de característica no tienen éxito/fracaso.
        Son puntos de inflexión narrativos.
        
        Returns:
            Siempre None (no hay resultado numérico)
        """
        return None
    
    def aplicar_consecuencias(self,
                             personaje: List,
                             resultado: Optional[ResultadoEvento]) -> None:
        """
        Registra la característica en el personaje.
        Guarda el registro en RESERVADO1 como una lista de diccionarios.
        
        CORREGIDO: Este método ahora está implementado correctamente.
        """
        # Crear registro como diccionario
        registro = {
            "fuerza": self.fuerza,
            "es_bendicion": self.es_bendicion,
            "efecto": self.efecto,
            "evento_id": self.id,
            "timestamp": datetime.now().timestamp(),
            "activo": True
        }
        
        # Asegurar que el personaje tiene el índice RESERVADO1
        if len(personaje) <= IndicesPersonaje.RESERVADO1:
            while len(personaje) <= IndicesPersonaje.RESERVADO1:
                personaje.append(None)
        
        # Obtener el valor actual de RESERVADO1
        valor_actual = personaje[IndicesPersonaje.RESERVADO1]
        
        # Si es None, crear nueva lista
        if valor_actual is None:
            personaje[IndicesPersonaje.RESERVADO1] = [registro]
        
        # Si es una lista, añadir a ella
        elif isinstance(valor_actual, list):
            personaje[IndicesPersonaje.RESERVADO1].append(registro)
        
        # Si es un entero (error de versión anterior), convertir a lista
        elif isinstance(valor_actual, int):
            contador = valor_actual
            personaje[IndicesPersonaje.RESERVADO1] = []
            # Preservar el contador viejo si es necesario
            if contador > 0:
                personaje[IndicesPersonaje.RESERVADO1].append({
                    "fuerza": "Histórico",
                    "es_bendicion": False,
                    "efecto": f"caracteristicas_antiguas_{contador}",
                    "evento_id": "legacy",
                    "timestamp": 0,
                    "activo": True
                })
            personaje[IndicesPersonaje.RESERVADO1].append(registro)
        
        # Cualquier otro tipo, reemplazar
        else:
            personaje[IndicesPersonaje.RESERVADO1] = [registro]
    
    def obtener_variante_aleatoria(self) -> str:
        """
        Selecciona una variante narrativa aleatoria.
        
        Returns:
            Una de las variantes disponibles
        """
        return random.choice(self.variantes) if self.variantes else self.descripcion


# ============================================================================
# GESTOR DE CARACTERÍSTICAS
# ============================================================================

class GestorCaracteristicas(GestorEventosBase):
    """
    Gestor especializado en eventos de características.
    Además de cargar eventos, proporciona métodos para listar características.
    """
    
    def __init__(self):
        super().__init__()
        self.nombre_gestor = "Características"
        self.eventos_por_fuerza = {}  # Índice rápido por fuerza
    
    def _procesar_json(self, data: Dict) -> None:
        """
        Procesa el JSON de eventos de características.
        """
        eventos_data = data.get('eventos', [])
        
        for ev_data in eventos_data:
            evento = self._crear_evento_desde_json(ev_data)
            if evento:
                self.eventos.append(evento)
                self.eventos_por_fuerza[evento.fuerza] = evento
    
    def _crear_evento_desde_json(self, ev_data: Dict) -> Optional[EventoCaracteristica]:
        """
        Crea un evento de característica desde JSON.
        """
        return EventoCaracteristica(
            id_evento=ev_data.get('id', ''),
            nombre=ev_data.get('nombre', ''),
            descripcion=ev_data.get('descripcion', ''),
            variantes=ev_data.get('variantes', []),
            fuerza=ev_data.get('fuerza', ''),
            es_bendicion=ev_data.get('es_bendicion', True),
            efecto=ev_data.get('efecto', '')
        )
    
    def obtener_por_fuerza(self, fuerza: str) -> Optional[EventoCaracteristica]:
        """Obtiene un evento por el nombre de la fuerza."""
        return self.eventos_por_fuerza.get(fuerza)
    
    def obtener_descripcion_completa(self, 
                                     evento: EventoCaracteristica,
                                     personaje: List) -> str:
        """
        Genera una descripción narrativa del contacto.
        """
        variante = evento.obtener_variante_aleatoria()
        
        texto = f"[{evento.id}] {evento.nombre}\n"
        texto += f"  {variante}\n"
        
        if evento.es_bendicion:
            texto += f"  ✨ Bendición: {evento.fuerza}\n"
        else:
            texto += f"  🌑 Maldición: {evento.fuerza}\n"
        
        texto += f"  Efecto: {evento.efecto}\n"
        
        return texto
    
    def listar_caracteristicas_personaje(self, personaje: List) -> List[str]:
        """
        Lista todas las características activas de un personaje.
        """
        if len(personaje) <= IndicesPersonaje.RESERVADO1:
            return []
        
        chars = personaje[IndicesPersonaje.RESERVADO1]
        if not chars or not isinstance(chars, list):
            return []
        
        resultado = []
        for reg in chars:
            if isinstance(reg, dict):
                estado = "✅" if reg.get('es_bendicion', False) else "⚠️"
                resultado.append(f"{estado} {reg.get('fuerza', 'Desconocida')} ({reg.get('efecto', '?')})")
            elif hasattr(reg, 'fuerza'):
                estado = "✅" if reg.es_bendicion else "⚠️"
                resultado.append(f"{estado} {reg.fuerza} ({reg.efecto})")
        
        return resultado
    
    def contar_bendiciones_maldiciones(self, personajes: List[List]) -> Dict[str, int]:
        """
        Cuenta el total de bendiciones y maldiciones en una lista de personajes.
        Útil para estadísticas.
        """
        bendiciones = 0
        maldiciones = 0
        
        for p in personajes:
            if len(p) <= IndicesPersonaje.RESERVADO1:
                continue
            
            chars = p[IndicesPersonaje.RESERVADO1]
            if not chars or not isinstance(chars, list):
                continue
            
            for reg in chars:
                if isinstance(reg, dict):
                    if reg.get('es_bendicion', False):
                        bendiciones += 1
                    else:
                        maldiciones += 1
                elif hasattr(reg, 'es_bendicion'):
                    if reg.es_bendicion:
                        bendiciones += 1
                    else:
                        maldiciones += 1
        
        return {"bendiciones": bendiciones, "maldiciones": maldiciones}


# ============================================================================
# PRUEBAS RÁPIDAS
# ============================================================================

if __name__ == "__main__":
    print("🧪 Probando GestorCaracteristicas (versión corregida)...")
    
    # Crear gestor
    gestor = GestorCaracteristicas()
    
    # Crear evento de prueba
    evento = EventoCaracteristica(
        id_evento="C1",
        nombre="El árbol sagrado",
        descripcion="Un árbol milenario te concede una bendición",
        variantes=["Roble ancestral", "Sauce llorón"],
        fuerza="Bendición de la Vida",
        es_bendicion=True,
        efecto="resistencia_enfermedades"
    )
    
    print(f"✅ Evento creado: {evento.nombre}")
    
    # Crear personaje de prueba
    from modulos.gestor_personajes import GestorPersonajes
    gp = GestorPersonajes()
    gp.cargar_desde_ejemplo(1)
    personaje = gp.obtener_personaje_aleatorio()
    
    if personaje:
        print(f"\n📊 Personaje: {personaje[IndicesPersonaje.RAZA]}")
        
        # Probar cálculo de resultado (debe ser None)
        resultado = evento.calcular_resultado(personaje)
        print(f"Resultado: {resultado} (esperado: None)")
        
        # Probar aplicación de consecuencias
        evento.aplicar_consecuencias(personaje, None)
        print(f"✅ Característica aplicada")
        
        # Verificar que se guardó
        chars = gestor.listar_caracteristicas_personaje(personaje)
        print(f"📋 Características: {chars}")
    
    print("\n✅ Pruebas completadas")