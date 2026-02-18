from dataclasses import dataclass

@dataclass
class Personaje:
    nombre: str
    edad: int
    habilidad: str
    fuerza: int
    inteligencia: int
    destreza: int

    def hablar(self):
        return f"Hola, soy {self.nombre}."

    def atacar(self):
        return f"{self.nombre} ataca con una fuerza de {self.fuerza}!"