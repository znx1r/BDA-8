from dataclasses import dataclass
import datetime

# ----------------------------------------
# |  Entidades de la base de datos       |
# ----------------------------------------
# | Profesores | PK = ID                 |
# | Alumnos    | PK = ID                 |
# | Cursos     | PK = ID                 |
# | Matriculas | PK = (AlumnoID, CursoID)|
# ----------------------------------------

@dataclass
class Profesores():
    id: str
    nombre: str

    def __str__(self):
        return f"ID: {self.id} - NOMBRE: {self.nombre}"

@dataclass
class Alumnos():
    id: str
    nombre: str
    email: str
    saldo: float = 500.00

    def __str__(self):
        return f"ID: {self.id} - NOMBRE: {self.nombre} - CORREO: {self.email}"

@dataclass
class Cursos():
    id: str
    nombre: str
    profesor_id: str
    precio: float = 100.00
    max_alumnos: int = 30
    nombre_en: str = ""

    def __str__(self):
        return f"ID: {self.id} - NOMBRE: {self.nombre} - PROFESOR_ID: {self.profesor_id}"

@dataclass
class Matriculas():
    alumno_id: str
    curso_id: str
    created_at: datetime.datetime

