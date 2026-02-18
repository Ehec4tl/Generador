"""
gestor_atributos.py - Eventos que desarrollan atributos específicos.
Versión con sistema d100 para dar protagonismo al azar.
"""

import random
from typing import List, Dict, Any, Optional, Tuple

from modulos.gestor_eventos import (
    Evento, TipoEvento, ResultadoEvento, 
    GestorEventosBase, obtener_indice_atributo,
    recalcular_suma_total, asegurar_no_negativo
)
from modulos.gestor_personajes import IndicesPersonaje


# ============================================================================
# CONSTANTES PARA UMBRALES (ajustables)
# ============================================================================

class UmbralesD100:
    """Define los umbrales para el sistema d100."""
    
    # Umbrales de tirada total
    EXITO_EPICO = 150  # ≥ 150 → éxito épico (+3)
    EXITO = 100        # ≥ 100 → éxito (+1)
    NORMAL = 60        # ≥ 60 → normal (0)
    FRACASO = 30       # ≥ 30 → fracaso (-1)
    # < 30 → fracaso épico (-3)
    
    # Los críticos naturales (100) y pifias (1) tienen prioridad


# ============================================================================
# EVENTOS DE ATRIBUTO (implementación con d100)
# ============================================================================

class EventoAtributo(Evento):
    """
    Evento que usa sistema d100:
    - Tirada d100 (1-100)
    - + (atributo_principal // 2)
    - + (atributo_secundario // 4) si existe
    """
    
    def __init__(self,
                 id_evento: str,
                 nombre: str,
                 descripcion: str,
                 variantes: List[str],
                 atributo_principal: str,
                 atributo_secundario: Optional[str] = None):
        """
        Inicializa un evento de atributo.
        
        Args:
            id_evento: Identificador (A1, A2, etc.)
            nombre: Nombre del evento
            descripcion: Descripción base
            variantes: Lista de descripciones alternativas
            atributo_principal: Atributo que contribuye al resultado
            atributo_secundario: Atributo que contribuye secundariamente
        """
        super().__init__(id_evento, nombre, descripcion, variantes)
        self.tipo = TipoEvento.ATRIBUTO
        self.atributo_principal = atributo_principal
        self.atributo_secundario = atributo_secundario
        
        # Cache de índices
        self.idx_principal = obtener_indice_atributo(atributo_principal)
        self.idx_secundario = (obtener_indice_atributo(atributo_secundario) 
                               if atributo_secundario else None)
        
        # Para depuración
        self.ultima_tirada = None
        self.prob_muerte = 0.3  # valor por defecto (se sobreescribe desde main)
    
    def calcular_resultado(self, personaje: List) -> ResultadoEvento:
        """
        Calcula el resultado usando sistema d100:
        - Tirada d100 (1-100)
        - + (atributo_principal // 2)
        - + (atributo_secundario // 4)
        """
        # Obtener valores de atributos
        valor_principal = personaje[self.idx_principal]
        
        if self.idx_secundario is not None:
            valor_secundario = personaje[self.idx_secundario]
            contrib_secundario = valor_secundario // 4
        else:
            contrib_secundario = 0
        
        # Contribuciones
        contrib_principal = valor_principal // 2
        tirada = random.randint(1, 100)
        
        # Total
        total = tirada + contrib_principal + contrib_secundario
        
        # Guardar para depuración
        self.ultima_tirada = {
            "dado": tirada,
            "principal": contrib_principal,
            "secundario": contrib_secundario,
            "total": total,
            "valor_principal": valor_principal,
            "valor_secundario": valor_secundario if self.idx_secundario else 0
        }
        
        # Determinar resultado (los críticos naturales tienen prioridad)
        if tirada == 100:
            return ResultadoEvento.EXITO_EPICO
        elif tirada == 1:
            return ResultadoEvento.FRACASO_EPICO
        elif total >= UmbralesD100.EXITO_EPICO:
            return ResultadoEvento.EXITO_EPICO
        elif total >= UmbralesD100.EXITO:
            return ResultadoEvento.EXITO
        elif total >= UmbralesD100.NORMAL:
            return ResultadoEvento.NORMAL
        elif total >= UmbralesD100.FRACASO:
            return ResultadoEvento.FRACASO
        else:
            return ResultadoEvento.FRACASO_EPICO
    
    def aplicar_consecuencias(self,
                             personaje: List,
                             resultado: Optional[ResultadoEvento]) -> None:
        """
        Aplica los cambios según el resultado.
        """
        if resultado is None:
            return
        
        # Aplicar al atributo principal
        personaje[self.idx_principal] += resultado.value
        asegurar_no_negativo(personaje, self.idx_principal)
        
        # Aplicar al secundario si existe y el resultado es ±3
        if self.idx_secundario is not None and abs(resultado.value) >= 3:
            # El secundario recibe ±1 (para ±3)
            cambio_secundario = 1 if resultado.value > 0 else -1
            personaje[self.idx_secundario] += cambio_secundario
            asegurar_no_negativo(personaje, self.idx_secundario)
        
        # Recalcular suma total
        recalcular_suma_total(personaje)
    
    def probar_muerte(self, personaje: List, resultado: ResultadoEvento) -> bool:
        """
        Determina si el personaje muere en un fracaso épico.
        """
        if resultado != ResultadoEvento.FRACASO_EPICO:
            return False
        
        # Usar la probabilidad de muerte configurada
        return random.random() < self.prob_muerte
    
    def obtener_descripcion_tirada(self) -> str:
        """Devuelve una descripción de la última tirada (para depuración)."""
        if not self.ultima_tirada:
            return "Sin tirada registrada"
        
        t = self.ultima_tirada
        return (f"d100: {t['dado']} + "
                f"({t['valor_principal']}//2={t['principal']}) + "
                f"({t['valor_secundario']}//4={t['secundario']}) = "
                f"{t['total']}")


# ============================================================================
# GESTOR DE EVENTOS DE ATRIBUTO
# ============================================================================

class GestorAtributos(GestorEventosBase):
    """
    Gestor especializado en eventos de atributos.
    """
    
    def __init__(self):
        super().__init__()
        self.nombre_gestor = "Atributos"
    
    def _procesar_json(self, data: Dict) -> None:
        """
        Procesa el JSON de eventos de atributos.
        """
        eventos_data = data.get('eventos', [])
        
        for ev_data in eventos_data:
            evento = self._crear_evento_desde_json(ev_data)
            if evento:
                self.eventos.append(evento)
    
    def _crear_evento_desde_json(self, ev_data: Dict) -> Optional[Evento]:
        """
        Crea un evento desde JSON.
        """
        return EventoAtributo(
            id_evento=ev_data.get('id', ''),
            nombre=ev_data.get('nombre', ''),
            descripcion=ev_data.get('descripcion', ''),
            variantes=ev_data.get('variantes', []),
            atributo_principal=ev_data.get('atributo_principal', 'F'),
            atributo_secundario=ev_data.get('atributo_secundario')
        )
    
    def obtener_descripcion_completa(self, 
                                     evento: EventoAtributo,
                                     personaje: List,
                                     resultado: ResultadoEvento,
                                     murio: bool = False) -> str:
        """
        Genera una descripción completa del evento con su resultado.
        Incluye detalles de la tirada.
        """
        variante = evento.obtener_variante_aleatoria()
        tirada_desc = evento.obtener_descripcion_tirada()
        
        texto = f"[{evento.id}] {evento.nombre}\n"
        texto += f"  {variante}\n"
        texto += f"  🎲 {tirada_desc}\n"
        
        # Describir resultado
        if resultado:
            if resultado == ResultadoEvento.EXITO_EPICO:
                texto += f"  🔥 ¡Éxito épico! +{resultado.value}\n"
            elif resultado == ResultadoEvento.EXITO:
                texto += f"  ✅ Éxito: +{resultado.value}\n"
            elif resultado == ResultadoEvento.NORMAL:
                texto += f"  ➡️ Normal: sin cambios\n"
            elif resultado == ResultadoEvento.FRACASO:
                texto += f"  ❌ Fracaso: {resultado.value}\n"
            elif resultado == ResultadoEvento.FRACASO_EPICO:
                texto += f"  💀 ¡Fracaso épico! {resultado.value}\n"
        
        if murio:
            texto += f"  ☠️ El personaje ha muerto en la aventura\n"
        
        return texto


# ============================================================================
# PRUEBAS RÁPIDAS
# ============================================================================

if __name__ == "__main__":
    print("🧪 Probando GestorAtributos con sistema d100...")
    
    # Crear gestor
    gestor = GestorAtributos()
    
    # Crear evento de prueba
    evento = EventoAtributo("A1", "Prueba", "Desc", ["Var"], "F", "RF")
    
    # Crear personaje de prueba
    from modulos.gestor_personajes import GestorPersonajes
    gp = GestorPersonajes()
    gp.cargar_desde_ejemplo(1)
    personaje = gp.obtener_personaje_aleatorio()
    
    if personaje:
        # Darle valores de prueba
        personaje[IndicesPersonaje.F_ABS] = 85
        personaje[IndicesPersonaje.RF_ABS] = 70
        
        print(f"\n📊 Personaje: F={personaje[IndicesPersonaje.F_ABS]}, RF={personaje[IndicesPersonaje.RF_ABS]}")
        
        # Simular varias tiradas
        for i in range(5):
            resultado = evento.calcular_resultado(personaje)
            print(f"\n  Tirada {i+1}: {evento.obtener_descripcion_tirada()}")
            print(f"  Resultado: {resultado.name}")
    
    print("\n✅ Pruebas completadas")