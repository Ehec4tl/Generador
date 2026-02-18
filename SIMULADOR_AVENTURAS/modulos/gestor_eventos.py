"""
gestor_eventos.py - Clases base para todos los eventos del simulador.
Define las estructuras comunes que usarán los módulos específicos.
"""

from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple


# ============================================================================
# ENUMS (constantes compartidas)
# ============================================================================

class TipoEvento(Enum):
    """Clasificación principal de eventos."""
    EQUIPO = "equipo"               # Eventos de obtención/mejora de equipo
    ATRIBUTO = "atributo"           # Eventos que desarrollan atributos
    CARACTERISTICA = "caracteristica"  # Eventos de contacto con fuerzas


class ResultadoEvento(Enum):
    """Posibles resultados de un evento con su valor numérico."""
    EXITO_EPICO = 3      # +3 al atributo
    EXITO = 1            # +1 al atributo
    NORMAL = 0           # Sin cambios
    FRACASO = -1         # -1 al atributo
    FRACASO_EPICO = -3   # -3 al atributo, posible muerte


# ============================================================================
# CLASE BASE ABSTRACTA
# ============================================================================

class Evento(ABC):
    """
    Clase base abstracta para TODOS los eventos.
    
    Cada tipo de evento (equipo, atributo, característica) heredará de esta clase
    e implementará sus propios métodos calcular_resultado() y aplicar_consecuencias().
    
    Atributos comunes:
        id_evento (str): Identificador único (ej: "E1", "A3", "C5")
        nombre (str): Nombre del evento
        descripcion (str): Descripción base
        variantes (List[str]): Lista de descripciones alternativas
        tipo (TipoEvento): Tipo de evento (se asigna en subclases)
    """
    
    def __init__(self, 
                 id_evento: str, 
                 nombre: str, 
                 descripcion: str, 
                 variantes: List[str]):
        """
        Inicializa un evento con sus datos básicos.
        
        Args:
            id_evento: Identificador único (ej: "E1", "A3")
            nombre: Nombre del evento
            descripcion: Descripción base
            variantes: Lista de descripciones alternativas
        """
        self.id = id_evento
        self.nombre = nombre
        self.descripcion = descripcion
        self.variantes = variantes
        self.tipo = None  # Se asignará en las subclases
        
        # Validación básica
        if not variantes:
            self.variantes = [descripcion]  # Usar descripción por defecto
    
    @abstractmethod
    def calcular_resultado(self, personaje: List) -> Optional[ResultadoEvento]:
        """
        Calcula el resultado del evento para un personaje específico.
        
        Args:
            personaje: Lista con los datos del personaje (formato de tu generador)
        
        Returns:
            ResultadoEvento o None si el evento no tiene éxito/fracaso
        """
        pass
    
    @abstractmethod
    def aplicar_consecuencias(self, 
                             personaje: List, 
                             resultado: Optional[ResultadoEvento]) -> None:
        """
        Aplica las consecuencias del evento al personaje.
        
        Args:
            personaje: Lista con los datos del personaje (se modifica in-place)
            resultado: Resultado del evento (puede ser None)
        """
        pass
    
    def obtener_variante_aleatoria(self) -> str:
        """
        Selecciona una variante narrativa aleatoria.
        
        Returns:
            Una de las variantes disponibles
        """
        import random
        return random.choice(self.variantes)
    
    def __repr__(self) -> str:
        """Representación legible del evento."""
        return f"Evento({self.id}: {self.nombre})"


# ============================================================================
# CLASE BASE PARA GESTORES DE EVENTOS
# ============================================================================

class GestorEventosBase:
    """
    Clase base para todos los gestores de eventos.
    
    Proporciona funcionalidad común para cargar eventos desde JSON
    y seleccionarlos aleatoriamente.
    """
    
    def __init__(self):
        self.eventos: List[Evento] = []
        self.nombre_gestor = "Base"
    
    def cargar_desde_json(self, archivo: str) -> int:
        """
        Carga eventos desde un archivo JSON.
        
        Args:
            archivo: Ruta al archivo JSON
        
        Returns:
            Número de eventos cargados
        """
        import json
        import os
        
        if not os.path.exists(archivo):
            print(f"  ⚠️ Archivo no encontrado: {archivo}")
            return 0
        
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Este método debe ser implementado por las subclases
            # porque cada tipo de evento tiene estructura diferente
            self._procesar_json(data)
            
            print(f"  ✅ {len(self.eventos)} eventos cargados desde {archivo}")
            return len(self.eventos)
            
        except Exception as e:
            print(f"  ❌ Error cargando {archivo}: {e}")
            return 0
    
    def _procesar_json(self, data: Dict) -> None:
        """
        Procesa el JSON específico de cada tipo de evento.
        Debe ser implementado por las subclases.
        """
        raise NotImplementedError("Las subclases deben implementar _procesar_json()")
    
    def obtener_evento_aleatorio(self) -> Optional[Evento]:
        """
        Selecciona un evento aleatorio de la lista.
        
        Returns:
            Un evento o None si no hay eventos
        """
        import random
        if not self.eventos:
            return None
        return random.choice(self.eventos)
    
    def obtener_evento_por_id(self, id_evento: str) -> Optional[Evento]:
        """
        Busca un evento por su ID.
        
        Args:
            id_evento: Identificador del evento
        
        Returns:
            El evento o None si no existe
        """
        for evento in self.eventos:
            if evento.id == id_evento:
                return evento
        return None
    
    def listar_eventos(self) -> None:
        """Muestra todos los eventos cargados."""
        print(f"\n📋 Eventos en {self.nombre_gestor}:")
        for evento in self.eventos:
            print(f"  • {evento.id}: {evento.nombre}")
            print(f"    Variantes: {len(evento.variantes)}")


# ============================================================================
# FUNCIONES AUXILIARES (compartidas por todos los módulos)
# ============================================================================

def obtener_indice_atributo(atributo: str) -> int:
    """
    Devuelve el índice en la lista de personaje para un atributo absoluto.
    
    Args:
        atributo: "F", "RM", "RF", "A", "I", "M", "E", "C"
    
    Returns:
        Índice en la lista (8, 10, 12, 14, 16, 18, 20, 22)
    """
    indices = {
        "F": 8, "RM": 10, "RF": 12, "A": 14,
        "I": 16, "M": 18, "E": 20, "C": 22
    }
    return indices.get(atributo, 8)  # Por defecto F si no existe


def recalcular_suma_total(personaje: List) -> None:
    """
    Recalcula la suma total de atributos (índice 23) después de cambios.
    
    Args:
        personaje: Lista del personaje (se modifica in-place)
    """
    indices_abs = [8, 10, 12, 14, 16, 18, 20, 22]
    personaje[23] = sum(personaje[i] for i in indices_abs)


def asegurar_no_negativo(personaje: List, indice: int) -> None:
    """
    Asegura que un atributo no sea negativo.
    
    Args:
        personaje: Lista del personaje
        indice: Índice del atributo a verificar
    """
    if personaje[indice] < 0:
        personaje[indice] = 0


# ============================================================================
# EJEMPLO DE USO (solo para pruebas)
# ============================================================================

if __name__ == "__main__":
    print("🔍 Probando módulo base de eventos...")
    
    # Verificar que los enums funcionan
    print(f"\nTipos de evento: {[t.value for t in TipoEvento]}")
    print(f"Resultados: {[(r.name, r.value) for r in ResultadoEvento]}")
    
    # Probar función auxiliar
    print(f"\nÍndice de F: {obtener_indice_atributo('F')}")
    print(f"Índice de C: {obtener_indice_atributo('C')}")
    
    print("\n✅ Módulo base OK")