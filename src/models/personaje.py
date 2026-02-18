from dataclasses import dataclass

@dataclass
class Personaje:
    nombre: str
    raza: str
    nivel: int
    clase: str

    # Definición de razas posibles
    RAZAS = ["Humano", "Elfo", "Enano", "Gigante", "Orcoide", "Hombre Bestia", "Constructo", "Mediano"]

    def __post_init__(self):
        if self.raza not in self.RAZAS:
            raise ValueError(f"Raza inválida: {self.raza}. Debe ser una de las siguientes: {', '.join(self.RAZAS)}")

    def __str__(self):
        return f"{self.nombre} es un {self.raza} de nivel {self.nivel} y clase {self.clase}."