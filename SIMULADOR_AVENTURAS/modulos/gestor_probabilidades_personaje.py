"""
gestor_probabilidades_personaje.py - Calcula probabilidades de eventos
basadas en los atributos y clase del personaje.
"""

import json
import random
from typing import Dict, List, Optional

from modulos.gestor_personajes import IndicesPersonaje


class CalculadorProbabilidades:
    """
    Calcula las probabilidades de cada tipo de evento para un personaje.
    """
    
    # Pesos base (suman 100)
    PESOS_BASE = {
        "combate": 20,
        "magia": 20,
        "exploracion": 20,
        "social": 20,
        "mistico": 20
    }
    
    # Modificadores por clase (se cargarán desde JSON)
    MOD_CLASE = {}
    
    def __init__(self, archivo_clases: Optional[str] = None):
        if archivo_clases:
            self.cargar_modificadores_clase(archivo_clases)
    
    def cargar_modificadores_clase(self, archivo_clases: str):
        """
        Carga los modificadores desde el archivo de clases.
        """
        try:
            with open(archivo_clases, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Procesar clases simples
            for key, clase in data.get("clases_simples", {}).items():
                self._agregar_modificador_clase(clase["nombre"], key)
            
            # Procesar clases dobles
            for key, clase in data.get("clases_dobles", {}).items():
                self._agregar_modificador_clase(clase["nombre"], key)
            
            # Procesar clases dobles puras
            for key, clase in data.get("clases_dobles_puras", {}).items():
                self._agregar_modificador_clase(clase["nombre"], key)
                
        except Exception as e:
            print(f"⚠️ Error cargando modificadores de clase: {e}")
            # Usar modificadores por defecto si falla la carga
            self._cargar_modificadores_por_defecto()
    
    def _agregar_modificador_clase(self, nombre_clase: str, key: str):
        """
        Asigna un modificador según los atributos de la clase.
        """
        # Determinar categoría según los atributos en la key
        if "_" in key:
            attr1, attr2 = key.split("_")
            atributos = [attr1, attr2]
        else:
            atributos = [key]
        
        # Calcular modificadores basados en atributos
        mod = {"combate": 0, "magia": 0, "exploracion": 0, "social": 0, "mistico": 0}
        
        for attr in atributos:
            if attr in ["F", "RF"]:
                mod["combate"] += 3
            elif attr in ["RM", "M"]:
                mod["magia"] += 3
            elif attr in ["A", "I"]:
                mod["exploracion"] += 3
            elif attr in ["E", "C"]:
                # E y C pueden ser social o místico según contexto
                if attr == "E":
                    mod["mistico"] += 2
                    mod["social"] += 1
                else:  # C
                    mod["social"] += 3
        
        # Normalizar: si hay dos atributos, promediar
        if len(atributos) == 2:
            for k in mod:
                mod[k] = mod[k] // 2
        
        self.MOD_CLASE[nombre_clase] = mod
    
    def _cargar_modificadores_por_defecto(self):
        """
        Carga modificadores por defecto si no se pudo leer el JSON.
        """
        self.MOD_CLASE = {
            "Guerrero": {"combate": +5, "magia": -2, "exploracion": 0, "social": -2, "mistico": -1},
            "Mago": {"combate": -2, "magia": +5, "exploracion": 0, "social": -2, "mistico": -1},
            "Explorador": {"combate": 0, "magia": -2, "exploracion": +5, "social": -2, "mistico": -1},
        }
    
    def calcular_pesos(self, personaje: List) -> Dict[str, float]:
        """
        Calcula los pesos para cada categoría basado en el personaje.
        
        Args:
            personaje: Lista en formato de IndicesPersonaje
        
        Returns:
            Dict con pesos normalizados para cada categoría
        """
        pesos = self.PESOS_BASE.copy()
        
        # 1. Modificadores por atributos
        pesos = self._aplicar_modificadores_atributos(personaje, pesos)
        
        # 2. Modificadores por clase
        pesos = self._aplicar_modificadores_clase(personaje, pesos)
        
        # 3. Normalizar a 100
        return self._normalizar(pesos)
    
    def _aplicar_modificadores_atributos(self, personaje: List, pesos: Dict) -> Dict:
        """+1 cada 10 puntos sobre 50 en atributos relacionados."""
        
        # Combate: F y RF
        f_val = personaje[IndicesPersonaje.F_ABS]
        rf_val = personaje[IndicesPersonaje.RF_ABS]
        pesos["combate"] += max(0, (f_val - 50) // 10)
        pesos["combate"] += max(0, (rf_val - 50) // 10)
        
        # Magia: RM y M
        rm_val = personaje[IndicesPersonaje.RM_ABS]
        m_val = personaje[IndicesPersonaje.M_ABS]
        pesos["magia"] += max(0, (rm_val - 50) // 10)
        pesos["magia"] += max(0, (m_val - 50) // 10)
        
        # Exploración: A e I
        a_val = personaje[IndicesPersonaje.A_ABS]
        i_val = personaje[IndicesPersonaje.I_ABS]
        pesos["exploracion"] += max(0, (a_val - 50) // 10)
        pesos["exploracion"] += max(0, (i_val - 50) // 10)
        
        # Social: E y C
        e_val = personaje[IndicesPersonaje.E_ABS]
        c_val = personaje[IndicesPersonaje.C_ABS]
        pesos["social"] += max(0, (e_val - 50) // 10)
        pesos["social"] += max(0, (c_val - 50) // 10)
        
        # Místico: E también aporta aquí (pero ya lo usamos en social)
        # Dejamos que E contribuya también a místico (doble propósito)
        pesos["mistico"] += max(0, (e_val - 50) // 15)  # Mitad de contribución
        
        return pesos
    
    def _aplicar_modificadores_clase(self, personaje: List, pesos: Dict) -> Dict:
        """Aplica modificadores según la clase del personaje."""
        
        clase = personaje[IndicesPersonaje.CLASE]
        if clase in self.MOD_CLASE:
            mods = self.MOD_CLASE[clase]
            for cat, valor in mods.items():
                if cat in pesos:
                    pesos[cat] += valor
        
        return pesos
    
    def _normalizar(self, pesos: Dict) -> Dict[str, float]:
        """Normaliza los pesos para que sumen 100."""
        total = sum(pesos.values())
        if total <= 0:
            return self.PESOS_BASE.copy()
        
        return {k: (v / total) * 100 for k, v in pesos.items()}
    
    def seleccionar_categoria(self, pesos: Dict[str, float]) -> str:
        """
        Selecciona una categoría según los pesos calculados.
        
        Returns:
            str: Categoría seleccionada ("combate", "magia", etc.)
        """
        categorias = list(pesos.keys())
        probabilidades = list(pesos.values())
        return random.choices(categorias, weights=probabilidades)[0]
    
    def obtener_probabilidades_legibles(self, pesos: Dict[str, float]) -> str:
        """Devuelve string legible con las probabilidades."""
        resultado = []
        for cat, prob in sorted(pesos.items(), key=lambda x: x[1], reverse=True):
            resultado.append(f"{cat}: {prob:.1f}%")
        return " | ".join(resultado)