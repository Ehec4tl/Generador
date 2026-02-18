"""
gestor_personajes.py - Manejo de personajes para el simulador de aventuras.
Carga personajes desde tu generador, añade campos de simulación y los mantiene.
"""

import random
from typing import List, Dict, Any, Optional, Tuple
from copy import deepcopy


# ============================================================================
# CONFIGURACIÓN DE ÍNDICES (basado en tu formato)
# ============================================================================

class IndicesPersonaje:
    """
    Define los índices de cada campo en la lista de personaje.
    Usando tu formato actual:
    [0:Código, 1:Raza, 2:Subraza, 3:MyB, 4:Variante, 5:Clase, 6:Clave_Clase,
     7:F_val, 8:F_abs, 9:RM_val, 10:RM_abs, 11:RF_val, 12:RF_abs,
     13:A_val, 14:A_abs, 15:I_val, 16:I_abs, 17:M_val, 18:M_abs,
     19:E_val, 20:E_abs, 21:C_val, 22:C_abs, 23:Suma_Total, 24:Tipo]
    """
    
    # Campos base (de tu generador)
    CODIGO = 0
    RAZA = 1
    SUBRAZA = 2
    MYB = 3
    VARIANTE = 4
    CLASE = 5
    CLAVE_CLASE = 6
    F_VAL = 7
    F_ABS = 8
    RM_VAL = 9
    RM_ABS = 10
    RF_VAL = 11
    RF_ABS = 12
    A_VAL = 13
    A_ABS = 14
    I_VAL = 15
    I_ABS = 16
    M_VAL = 17
    M_ABS = 18
    E_VAL = 19
    E_ABS = 20
    C_VAL = 21
    C_ABS = 22
    SUMA_TOTAL = 23
    TIPO = 24
    
    # Campos de simulación (se añadirán al final)
    EVENTOS_VIDA = 25  # Contador de eventos vividos
    VICTORIAS = 26     # Victorias en eventos
    DERROTAS = 27      # Derrotas en eventos
    VIVO = 28          # Booleano: True si vive
    RESERVADO1 = 29    # Para futura expansión
    RESERVADO2 = 30    # Para futura expansión
    
    # Lista de atributos absolutos para iterar fácilmente
    ATRIBUTOS_ABS = [F_ABS, RM_ABS, RF_ABS, A_ABS, I_ABS, M_ABS, E_ABS, C_ABS]
    
    @classmethod
    def get_nombre_atributo(cls, indice: int) -> str:
        """Devuelve el nombre del atributo dado su índice."""
        mapa = {
            cls.F_ABS: "F", cls.RM_ABS: "RM", cls.RF_ABS: "RF",
            cls.A_ABS: "A", cls.I_ABS: "I", cls.M_ABS: "M",
            cls.E_ABS: "E", cls.C_ABS: "C"
        }
        return mapa.get(indice, "?")


# ============================================================================
# GESTOR PRINCIPAL DE PERSONAJES
# ============================================================================

class GestorPersonajes:
    """
    Gestiona toda la información de los personajes durante la simulación.
    
    Responsabilidades:
    - Cargar personajes desde tu generador
    - Añadir campos necesarios para la simulación
    - Mantener listas de vivos y muertos
    - Guardar resultados
    """
    
    def __init__(self):
        self.personajes_originales = []  # Copia de seguridad
        self.personajes = []              # Personajes activos (con campos extra)
        self.personajes_muertos = []      # Historial de bajas
        
        # Estadísticas
        self.total_cargados = 0
        self.campos_anadidos = 0
    
    def cargar_desde_generador(self, personajes_generados: List[List]) -> int:
        """
        Carga personajes desde tu generador (lectorv4.py) y los prepara.
        
        Args:
            personajes_generados: Lista en tu formato original
        
        Returns:
            Número de personajes cargados
        """
        self.personajes_originales = deepcopy(personajes_generados)
        self.personajes = []
        
        for p in personajes_generados:
            # Crear copia para no modificar el original
            personaje = p.copy()
            
            # Añadir campos de simulación
            personaje.append(0)   # EVENTOS_VIDA
            personaje.append(0)   # VICTORIAS
            personaje.append(0)   # DERROTAS
            personaje.append(True) # VIVO
            personaje.append(None) # RESERVADO1
            personaje.append(None) # RESERVADO2
            
            self.personajes.append(personaje)
        
        self.total_cargados = len(self.personajes)
        self.campos_anadidos = 6  # Los 6 campos nuevos
        
        print(f"\n📦 Personajes cargados:")
        print(f"  • Originales: {len(personajes_generados)}")
        print(f"  • Preparados: {len(self.personajes)}")
        print(f"  • Campos totales: {len(self.personajes[0]) if self.personajes else 0}")
        
        return len(self.personajes)
    
    def cargar_desde_ejemplo(self, num_ejemplos: int = 5) -> int:
        """
        Carga personajes de ejemplo para pruebas sin tu generador.
        
        Args:
            num_ejemplos: Número de personajes de prueba
        
        Returns:
            Número de personajes cargados
        """
        ejemplos = []
        for i in range(num_ejemplos):
            # Crear personaje mínimo
            p = [
                f"TEST{i:04d}",           # Código
                random.choice(["Humano", "Elfo", "Enano"]),  # Raza
                random.choice(["Nevado", "Oscuro", "Montaña"]),  # Subraza
                random.choice(["Bendición", "Maldición", "Ninguna"]),  # MyB
                "Variante",                 # Variante
                random.choice(["Guerrero", "Mago", "Explorador"]),  # Clase
                "key",                       # Clave_Clase
                5, 50, 5, 50, 5, 50,         # F_val, F_abs, RM_val, RM_abs, RF_val, RF_abs
                5, 50, 5, 50, 5, 50,         # A_val, A_abs, I_val, I_abs, M_val, M_abs
                5, 50, 5, 50,                 # E_val, E_abs, C_val, C_abs
                400,                          # Suma_Total
                "Normal"                      # Tipo
            ]
            ejemplos.append(p)
        
        return self.cargar_desde_generador(ejemplos)
    
    def obtener_vivos(self) -> List[List]:
        """Devuelve lista de personajes vivos."""
        return [p for p in self.personajes if p[IndicesPersonaje.VIVO]]
    
    def obtener_muertos(self) -> List[List]:
        """Devuelve lista de personajes muertos."""
        return self.personajes_muertos
    
    def obtener_personaje_aleatorio(self) -> Optional[List]:
        """
        Selecciona un personaje vivo al azar.
        
        Returns:
            Un personaje o None si no hay vivos
        """
        vivos = self.obtener_vivos()
        if not vivos:
            return None
        return random.choice(vivos)
    
    def obtener_personaje_por_indice(self, idx: int) -> Optional[List]:
        """
        Obtiene un personaje por su índice en la lista.
        
        Args:
            idx: Índice en self.personajes
        
        Returns:
            El personaje o None si no existe
        """
        if 0 <= idx < len(self.personajes):
            return self.personajes[idx]
        return None
    
    def marcar_como_muerto(self, personaje: List) -> bool:
        """
        Marca un personaje como muerto y lo mueve al historial.
        
        Args:
            personaje: El personaje a marcar
        
        Returns:
            True si se marcó correctamente
        """
        if not personaje[IndicesPersonaje.VIVO]:
            return False  # Ya estaba muerto
        
        personaje[IndicesPersonaje.VIVO] = False
        self.personajes_muertos.append(personaje)
        
        # No lo eliminamos de personajes, solo lo marcamos
        return True
    
    def aplicar_cambio_atributo(self, 
                                 personaje: List, 
                                 atributo: str, 
                                 cambio: int) -> int:
        """
        Aplica un cambio a un atributo específico.
        
        Args:
            personaje: El personaje a modificar
            atributo: "F", "RM", "RF", "A", "I", "M", "E", "C"
            cambio: Valor a sumar (puede ser negativo)
        
        Returns:
            Nuevo valor del atributo
        """
        idx = self._indice_atributo(atributo)
        if idx is None:
            return 0
        
        # Aplicar cambio
        personaje[idx] = max(0, personaje[idx] + cambio)
        
        # Recalcular suma total
        self._recalcular_suma(personaje)
        
        return personaje[idx]
    
    def aplicar_cambio_multiple(self,
                                 personaje: List,
                                 cambios: Dict[str, int]) -> None:
        """
        Aplica múltiples cambios a la vez.
        
        Args:
            personaje: El personaje a modificar
            cambios: Dict {atributo: cambio}
        """
        for attr, cambio in cambios.items():
            idx = self._indice_atributo(attr)
            if idx is not None:
                personaje[idx] = max(0, personaje[idx] + cambio)
        
        self._recalcular_suma(personaje)
    
    def _indice_atributo(self, atributo: str) -> Optional[int]:
        """Convierte nombre de atributo a índice."""
        mapa = {
            "F": IndicesPersonaje.F_ABS,
            "RM": IndicesPersonaje.RM_ABS,
            "RF": IndicesPersonaje.RF_ABS,
            "A": IndicesPersonaje.A_ABS,
            "I": IndicesPersonaje.I_ABS,
            "M": IndicesPersonaje.M_ABS,
            "E": IndicesPersonaje.E_ABS,
            "C": IndicesPersonaje.C_ABS
        }
        return mapa.get(atributo)
    
    def _recalcular_suma(self, personaje: List) -> None:
        """Recalcula la suma total de atributos."""
        suma = 0
        for idx in IndicesPersonaje.ATRIBUTOS_ABS:
            suma += personaje[idx]
        personaje[IndicesPersonaje.SUMA_TOTAL] = suma
    
    def registrar_evento(self, personaje: List, resultado_valor: int) -> None:
        """
        Registra que un personaje vivió un evento.
        
        Args:
            personaje: El personaje
            resultado_valor: Valor del resultado (positivo=victoria, negativo=derrota)
        """
        personaje[IndicesPersonaje.EVENTOS_VIDA] += 1
        if resultado_valor > 0:
            personaje[IndicesPersonaje.VICTORIAS] += 1
        elif resultado_valor < 0:
            personaje[IndicesPersonaje.DERROTAS] += 1
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Calcula estadísticas básicas de la población.
        
        Returns:
            Diccionario con estadísticas
        """
        vivos = self.obtener_vivos()
        
        stats = {
            "total_inicial": self.total_cargados,
            "vivos_actuales": len(vivos),
            "muertos": len(self.personajes_muertos),
            "total_eventos": sum(p[IndicesPersonaje.EVENTOS_VIDA] for p in self.personajes),
            "promedio_atributos": 0,
            "distribucion_razas": {},
            "distribucion_clases": {},
            "distribucion_tipos": {}
        }
        
        if vivos:
            # Promedio de suma total
            sumas = [p[IndicesPersonaje.SUMA_TOTAL] for p in vivos]
            stats["promedio_atributos"] = sum(sumas) / len(sumas)
            
            # Distribuciones
            for p in vivos:
                raza = p[IndicesPersonaje.RAZA]
                clase = p[IndicesPersonaje.CLASE]
                tipo = p[IndicesPersonaje.TIPO]
                
                stats["distribucion_razas"][raza] = stats["distribucion_razas"].get(raza, 0) + 1
                stats["distribucion_clases"][clase] = stats["distribucion_clases"].get(clase, 0) + 1
                stats["distribucion_tipos"][tipo] = stats["distribucion_tipos"].get(tipo, 0) + 1
        
        return stats
    
    def mostrar_resumen(self) -> None:
        """Muestra un resumen del estado actual."""
        stats = self.obtener_estadisticas()
        
        print("\n" + "="*50)
        print("📊 RESUMEN DE POBLACIÓN")
        print("="*50)
        print(f"Total inicial: {stats['total_inicial']}")
        print(f"Vivos: {stats['vivos_actuales']}")
        print(f"Muertos: {stats['muertos']}")
        print(f"Eventos totales: {stats['total_eventos']}")
        
        if stats['vivos_actuales'] > 0:
            print(f"\nPromedio de atributos: {stats['promedio_atributos']:.1f}")
            
            print("\nDistribución por raza:")
            for raza, count in sorted(stats['distribucion_razas'].items(), 
                                      key=lambda x: x[1], reverse=True):
                print(f"  • {raza}: {count}")
            
            print("\nDistribución por tipo:")
            for tipo, count in stats['distribucion_tipos'].items():
                print(f"  • {tipo}: {count}")


# ============================================================================
# PRUEBAS RÁPIDAS
# ============================================================================

if __name__ == "__main__":
    print("🧪 Probando GestorPersonajes...")
    
    # Crear gestor
    gestor = GestorPersonajes()
    
    # Cargar datos de ejemplo
    gestor.cargar_desde_ejemplo(10)
    
    # Mostrar estadísticas
    gestor.mostrar_resumen()
    
    # Probar selección aleatoria
    pj = gestor.obtener_personaje_aleatorio()
    if pj:
        print(f"\nPersonaje aleatorio: {pj[IndicesPersonaje.RAZA]} "
              f"{pj[IndicesPersonaje.SUBRAZA]} - {pj[IndicesPersonaje.CLASE]}")
    
    # Probar cambio de atributo
    if pj:
        f_antes = pj[IndicesPersonaje.F_ABS]
        gestor.aplicar_cambio_atributo(pj, "F", 10)
        f_despues = pj[IndicesPersonaje.F_ABS]
        print(f"Fuerza: {f_antes} → {f_despues}")
    
    print("\n✅ Pruebas completadas")