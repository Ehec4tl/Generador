"""
main.py - Orquestador principal del simulador de aventuras.
Versión INDIVIDUAL con probabilidades basadas en el personaje.
"""

import os
import sys
import random
from typing import List, Dict, Any, Optional

# Configuración de rutas
ruta_actual = os.path.dirname(os.path.abspath(__file__))
if ruta_actual not in sys.path:
    sys.path.insert(0, ruta_actual)

ruta_modulos = os.path.join(ruta_actual, "modulos")
if os.path.exists(ruta_modulos) and ruta_modulos not in sys.path:
    sys.path.insert(0, ruta_modulos)

# Importaciones
print("📦 Importando módulos...")
from modulos.gestor_personajes import GestorPersonajes, IndicesPersonaje
from modulos.gestor_eventos import TipoEvento, ResultadoEvento
from modulos.gestor_equipo import GestorEquipo
from modulos.gestor_atributos import GestorAtributos
from modulos.gestor_caracteristicas import GestorCaracteristicas
from modulos.gestor_resultados import GestorResultados
from modulos.gestor_probabilidades_personaje import CalculadorProbabilidades
print("✅ Módulos importados correctamente")


# ============================================================================
# CONFIGURACIÓN DE LA SIMULACIÓN
# ============================================================================

class ConfiguracionSimulacion:
    """Configuración global de la simulación."""
    
    def __init__(self):
        # Probabilidades base (se usarán como fallback)
        self.prob_equipo = 0.45      # 45% eventos de equipo
        self.prob_atributo = 0.45     # 45% eventos de atributos
        self.prob_caracteristica = 0.1  # 10% eventos de características (MyB)
        
        # Número de eventos POR PERSONAJE
        self.eventos_por_personaje = 5
        
        # Probabilidad de muerte en fracaso épico (0-1)
        self.prob_muerte = 0.1       # 10%
        
        # Mostrar detalles durante la simulación
        self.verbose = True
        
        # Guardar resultados automáticamente
        self.guardar_resultados = True
        
        # Nombre base para archivos de salida
        self.nombre_base = "aventuras_individual"
    
    def validar(self):
        """Valida que las probabilidades sumen 1.0."""
        total = self.prob_equipo + self.prob_atributo + self.prob_caracteristica
        if abs(total - 1.0) > 0.001:
            print(f"⚠️ Probabilidades no suman 1.0: {total}. Ajustando...")
            suma = total
            self.prob_equipo /= suma
            self.prob_atributo /= suma
            self.prob_caracteristica /= suma


# ============================================================================
# SIMULADOR PRINCIPAL (VERSIÓN INDIVIDUAL CON PROBABILIDADES PERSONALIZADAS)
# ============================================================================

class SimuladorAventuras:
    """
    Orquestador principal - Versión INDIVIDUAL.
    Cada personaje vive sus propias aventuras con probabilidades personalizadas.
    """
    
    def __init__(self, config: Optional[ConfiguracionSimulacion] = None):
        self.config = config or ConfiguracionSimulacion()
        self.config.validar()
        
        # Inicializar gestores
        self.gestor_pjs = GestorPersonajes()
        self.gestor_equipo = GestorEquipo()
        self.gestor_atributos = GestorAtributos()
        self.gestor_caracteristicas = GestorCaracteristicas()
        self.gestor_resultados = GestorResultados()
        
        # Inicializar calculador de probabilidades (con el archivo de clases)
        try:
            ruta_clases = os.path.join(ruta_actual, "clases.json")
            self.calculador_prob = CalculadorProbabilidades(ruta_clases)
            print("✅ Calculador de probabilidades inicializado")
        except Exception as e:
            print(f"⚠️ Error iniciando calculador de probabilidades: {e}")
            self.calculador_prob = None
        
        # Estado de la simulación
        self.eventos_ocurridos = []
        self.generacion_actual = 0
        self.historial_por_personaje = {}
    
    def cargar_eventos(self) -> bool:
        """Carga todos los eventos desde los archivos JSON."""
        print("\n📂 Cargando eventos...")
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        datos_dir = os.path.join(base_dir, "datos")
        
        archivos = [
            (self.gestor_equipo, "eventos_equipo.json", "Equipo"),
            (self.gestor_atributos, "eventos_atributos.json", "Atributos"),
            (self.gestor_caracteristicas, "eventos_caracteristicas.json", "Características")
        ]
        
        total_cargados = 0
        for gestor, archivo, nombre in archivos:
            ruta = os.path.join(datos_dir, archivo)
            if os.path.exists(ruta):
                count = gestor.cargar_desde_json(ruta)
                total_cargados += count
                if self.config.verbose:
                    print(f"  • {nombre}: {count} eventos")
            else:
                print(f"  ⚠️ No se encuentra {ruta}")
        
        print(f"✅ Total eventos cargados: {total_cargados}")
        return total_cargados > 0
    
    def cargar_personajes(self, desde_generador: bool = True, 
                         personajes_externos: Optional[List[List]] = None) -> int:
        """Carga los personajes para la simulación."""
        if personajes_externos:
            return self.gestor_pjs.cargar_desde_generador(personajes_externos)
        
        elif desde_generador:
            try:
                from lectorv4 import generate_characters
                print("\n🎲 Usando tu generador de personajes...")
                personajes = generate_characters()
                return self.gestor_pjs.cargar_desde_generador(personajes)
                
            except ImportError as e:
                print(f"  ⚠️ No se pudo importar lectorv4.py: {e}")
                print("  Usando personajes de ejemplo...")
                return self.gestor_pjs.cargar_desde_ejemplo(10)
        else:
            return self.gestor_pjs.cargar_desde_ejemplo(10)
    
    def seleccionar_tipo_evento(self) -> TipoEvento:
        """Selecciona un tipo de evento según las probabilidades base (fallback)."""
        tipos = [TipoEvento.EQUIPO, TipoEvento.ATRIBUTO, TipoEvento.CARACTERISTICA]
        pesos = [self.config.prob_equipo, self.config.prob_atributo, self.config.prob_caracteristica]
        return random.choices(tipos, weights=pesos)[0]
    
    def obtener_evento_por_tipo(self, tipo: TipoEvento):
        """Obtiene un evento aleatorio del tipo especificado (fallback)."""
        if tipo == TipoEvento.EQUIPO:
            return self.gestor_equipo.obtener_evento_aleatorio()
        elif tipo == TipoEvento.ATRIBUTO:
            return self.gestor_atributos.obtener_evento_aleatorio()
        else:
            return self.gestor_caracteristicas.obtener_evento_aleatorio()
    
    # ===== NUEVOS MÉTODOS PARA PROBABILIDADES PERSONALIZADAS =====
    
    def seleccionar_evento_para_personaje(self, personaje):
        """
        Selecciona un evento basado en las características del personaje.
        """
        # Si no hay calculador de probabilidades, usar método tradicional
        if not self.calculador_prob:
            tipo = self.seleccionar_tipo_evento()
            return self.obtener_evento_por_tipo(tipo)
        
        # Calcular pesos según el personaje
        pesos = self.calculador_prob.calcular_pesos(personaje)
        
        # Mostrar probabilidades (opcional, para depuración)
        if self.config.verbose:
            prob_str = self.calculador_prob.obtener_probabilidades_legibles(pesos)
            print(f"    📊 Probabilidades: {prob_str}")
        
        # Seleccionar categoría
        categoria = self.calculador_prob.seleccionar_categoria(pesos)
        
        # Mapear categoría a tipo de evento
        if categoria == "mistico":
            return self.gestor_caracteristicas.obtener_evento_aleatorio()
        else:
            # Para las demás categorías, filtrar eventos de atributo
            return self._obtener_evento_atributo_por_categoria(categoria)
    
    def _obtener_evento_atributo_por_categoria(self, categoria):
        """
        Filtra eventos de atributo por categoría.
        """
        # Mapeo de categoría a atributos principales
        atributos_por_categoria = {
            "combate": ["F", "RF"],
            "magia": ["RM", "M"],
            "exploracion": ["A", "I"],
            "social": ["E", "C"]
        }
        
        atributos = atributos_por_categoria.get(categoria, ["F"])
        
        # Filtrar eventos que tengan como principal alguno de estos atributos
        eventos_filtrados = [
            e for e in self.gestor_atributos.eventos
            if e.atributo_principal in atributos
        ]
        
        if eventos_filtrados:
            return random.choice(eventos_filtrados)
        else:
            # Fallback si no hay eventos de esa categoría
            return self.gestor_atributos.obtener_evento_aleatorio()
    
    # ===== MÉTODOS EXISTENTES MODIFICADOS =====
    
    def ejecutar_evento(self, evento, personaje) -> Dict:
        """Ejecuta un evento sobre un personaje y registra el resultado."""
        registro = {
            "tipo": evento.tipo.value if evento.tipo else "desconocido",
            "nombre": evento.nombre,
            "evento_id": evento.id,
            "personaje": f"{personaje[IndicesPersonaje.RAZA]} {personaje[IndicesPersonaje.SUBRAZA]}",
            "participantes": []
        }
        
        # Calcular resultado
        if evento.tipo == TipoEvento.CARACTERISTICA:
            resultado = None
            murio = False
        else:
            # Pasar la probabilidad de muerte al evento de atributo
            if hasattr(evento, 'prob_muerte'):
                evento.prob_muerte = self.config.prob_muerte
            
            resultado = evento.calcular_resultado(personaje)
            murio = False
            
            # Probar muerte (solo para eventos de atributo)
            if evento.tipo == TipoEvento.ATRIBUTO and hasattr(evento, 'probar_muerte'):
                murio = evento.probar_muerte(personaje, resultado)
        
        # Registrar antes de cambios
        antes = {
            "F": personaje[IndicesPersonaje.F_ABS],
            "suma": personaje[IndicesPersonaje.SUMA_TOTAL]
        }
        
        # Aplicar consecuencias
        evento.aplicar_consecuencias(personaje, resultado)
        
        # Registrar evento en el personaje
        if resultado:
            self.gestor_pjs.registrar_evento(
                personaje, 
                resultado.value if resultado else 0
            )
        
        # Marcar como muerto si aplica
        if murio:
            self.gestor_pjs.marcar_como_muerto(personaje)
        
        # Registrar participante
        registro["participantes"].append({
            "indice": id(personaje),
            "nombre": f"{personaje[IndicesPersonaje.RAZA]} {personaje[IndicesPersonaje.SUBRAZA]}",
            "resultado": resultado.name if resultado else "contacto",
            "murio": murio,
            "antes": antes,
            "despues": {
                "F": personaje[IndicesPersonaje.F_ABS],
                "suma": personaje[IndicesPersonaje.SUMA_TOTAL]
            }
        })
        
        return registro
    
    def simular_individual(self) -> List[Dict]:
        """
        Simulación INDIVIDUAL: cada personaje vive sus propias aventuras.
        """
        print("\n" + "="*60)
        print("⚔️ SIMULACIÓN INDIVIDUAL POR PERSONAJE ⚔️")
        print("="*60)
        print(f"Configuración:")
        print(f"  • Eventos por personaje: {self.config.eventos_por_personaje}")
        print(f"  • Probabilidad muerte: {self.config.prob_muerte*100:.0f}%")
        print(f"  • Usando probabilidades personalizadas: {self.calculador_prob is not None}")
        
        self.eventos_ocurridos = []
        personajes_vivos = self.gestor_pjs.obtener_vivos()
        
        print(f"\n📊 Personajes vivos iniciales: {len(personajes_vivos)}")
        
        # Estadísticas por personaje
        stats_personajes = {
            "eventos_vividos": [],
            "victorias": [],
            "derrotas": [],
            "contactos": []
        }
        
        for idx_pj, personaje in enumerate(personajes_vivos, 1):
            print(f"\n{'='*50}")
            print(f"👤 PERSONAJE {idx_pj}/{len(personajes_vivos)}")
            print(f"   {personaje[IndicesPersonaje.RAZA]} {personaje[IndicesPersonaje.SUBRAZA]} - {personaje[IndicesPersonaje.CLASE]}")
            print(f"   Atributos: F:{personaje[IndicesPersonaje.F_ABS]} | "
                  f"RM:{personaje[IndicesPersonaje.RM_ABS]} | "
                  f"RF:{personaje[IndicesPersonaje.RF_ABS]} | "
                  f"A:{personaje[IndicesPersonaje.A_ABS]}")
            print(f"   Suma total: {personaje[IndicesPersonaje.SUMA_TOTAL]}")
            print(f"{'='*50}")
            
            # Contadores para este personaje
            eventos_pj = 0
            victorias_pj = 0
            derrotas_pj = 0
            contactos_pj = 0
            
            # Este personaje vive N eventos
            for i in range(self.config.eventos_por_personaje):
                # Verificar si sigue vivo
                if not personaje[IndicesPersonaje.VIVO]:
                    print(f"\n  ⚰️ Personaje murió después de {i} eventos")
                    break
                
                # ===== CAMBIO IMPORTANTE: usar selección personalizada =====
                evento = self.seleccionar_evento_para_personaje(personaje)
                if not evento:
                    # Fallback si no hay evento
                    tipo = self.seleccionar_tipo_evento()
                    evento = self.obtener_evento_por_tipo(tipo)
                    if not evento:
                        continue
                
                eventos_pj += 1
                
                # Mostrar progreso
                print(f"\n  📌 Evento {i+1}/{self.config.eventos_por_personaje}: {evento.nombre}")
                
                # Ejecutar evento
                registro = self.ejecutar_evento(evento, personaje)
                self.eventos_ocurridos.append(registro)
                
                # Mostrar resultado
                if registro["participantes"]:
                    p = registro["participantes"][0]
                    print(f"    Resultado: {p['resultado']}")
                    
                    if p['resultado'] in ['EXITO', 'EXITO_EPICO']:
                        victorias_pj += 1
                    elif p['resultado'] in ['FRACASO', 'FRACASO_EPICO']:
                        derrotas_pj += 1
                    elif p['resultado'] == 'contacto':
                        contactos_pj += 1
                    
                    if p.get('murio'):
                        print(f"    💀 ¡HA MUERTO!")
                    print(f"    Suma: {p['antes']['suma']} → {p['despues']['suma']}")
                    
                    # Mostrar tirada si es evento de atributo
                    if hasattr(evento, 'obtener_descripcion_tirada'):
                        print(f"    🎲 {evento.obtener_descripcion_tirada()}")
            
            # Estadísticas del personaje
            stats_personajes["eventos_vividos"].append(eventos_pj)
            stats_personajes["victorias"].append(victorias_pj)
            stats_personajes["derrotas"].append(derrotas_pj)
            stats_personajes["contactos"].append(contactos_pj)
            
            print(f"\n  📊 Resumen {personaje[IndicesPersonaje.RAZA]}:")
            print(f"     Eventos: {eventos_pj} | Victorias: {victorias_pj} | Derrotas: {derrotas_pj} | Contactos: {contactos_pj}")
        
        print("\n" + "="*60)
        print("✅ SIMULACIÓN INDIVIDUAL COMPLETADA")
        print("="*60)
        
        vivos_finales = self.gestor_pjs.obtener_vivos()
        muertos = self.gestor_pjs.obtener_muertos()
        
        print(f"\n📊 ESTADÍSTICAS GLOBALES:")
        print(f"  • Eventos totales: {len(self.eventos_ocurridos)}")
        print(f"  • Personajes vivos: {len(vivos_finales)}")
        print(f"  • Personajes muertos: {len(muertos)}")
        
        if vivos_finales:
            print(f"\n  • Promedio eventos por personaje: {sum(stats_personajes['eventos_vividos'])/len(vivos_finales):.1f}")
            print(f"  • Promedio victorias: {sum(stats_personajes['victorias'])/len(vivos_finales):.1f}")
            print(f"  • Promedio derrotas: {sum(stats_personajes['derrotas'])/len(vivos_finales):.1f}")
        
        return self.eventos_ocurridos
    
    def generar_resultados(self):
        """Genera todos los resultados de la simulación."""
        self.gestor_resultados.cargar_datos(
            self.gestor_pjs.personajes_originales,
            self.gestor_pjs.personajes,
            self.eventos_ocurridos
        )
        
        self.gestor_resultados.mostrar_resumen()
        
        if self.config.guardar_resultados:
            self.gestor_resultados.exportar_a_excel(self.config.nombre_base)
            self.gestor_resultados.guardar_resumen_txt()


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    print("\n" + "="*60)
    print("🏰 SIMULADOR DE AVENTURAS INDIVIDUALES 🏰")
    print("="*60)
    
    # Crear configuración
    config = ConfiguracionSimulacion()
    
    # Permitir configuración interactiva
    print("\n📋 CONFIGURACIÓN")
    print("Presiona Enter para usar valores por defecto")
    
    try:
        num = input(f"Eventos por personaje (default: {config.eventos_por_personaje}): ")
        if num.strip():
            config.eventos_por_personaje = int(num)
        
        prob_muerte = input(f"Probabilidad de muerte en fracaso épico % (default: {config.prob_muerte*100:.0f}%): ")
        if prob_muerte.strip():
            config.prob_muerte = float(prob_muerte) / 100
        
    except ValueError:
        print("  Usando valores por defecto")
    
    # Crear simulador
    simulador = SimuladorAventuras(config)
    
    # Cargar eventos
    if not simulador.cargar_eventos():
        print("❌ Error: No se pudieron cargar eventos")
        return
    
    # Cargar personajes
    print("\n📦 CARGA DE PERSONAJES")
    print("1. Usar generador propio (lectorv4.py)")
    print("2. Usar personajes de ejemplo")
    
    opcion = input("Selecciona opción (1/2) [default: 1]: ").strip()
    
    if opcion == "2":
        simulador.cargar_personajes(desde_generador=False)
    else:
        personajes_cargados = simulador.cargar_personajes(desde_generador=True)
        if personajes_cargados == 0:
            print("  Usando personajes de ejemplo...")
            simulador.cargar_personajes(desde_generador=False)
    
    # Mostrar resumen inicial
    vivos = simulador.gestor_pjs.obtener_vivos()
    print(f"\n📊 POBLACIÓN INICIAL: {len(vivos)} personajes vivos")
    
    if len(vivos) == 0:
        print("❌ Error: No hay personajes para simular")
        return
    
    # Ejecutar simulación individual
    input("\nPresiona Enter para comenzar la simulación individual...")
    simulador.simular_individual()
    
    # Generar resultados
    simulador.generar_resultados()
    
    print("\n" + "="*60)
    print("🎉 SIMULACIÓN INDIVIDUAL FINALIZADA")
    print("="*60)


if __name__ == "__main__":
    main()