import psycopg2
from config import PG_HOST, PG_NAME, PG_USER, PG_PASSWORD, PG_PORT, SQLITE_PATH

# Conexión a PostgreSQL

PG_CONN = {
    "host":     PG_HOST,
    "database": PG_NAME,
    "user":     PG_USER,
    "password": PG_PASSWORD,
    "port":     PG_PORT,
}


def get_pg_conn():
    return psycopg2.connect(**PG_CONN)


def already_seeded(cur, table: str, min_rows: int) -> bool:
    cur.execute(f"SELECT COUNT(*) FROM {table};")
    return cur.fetchone()[0] >= min_rows


# Dataset mínimo PostgreSQL

PROFESORES_NOMBRES = [
    "Ana García López",      "Carlos Martínez Ruiz",  "Elena Sánchez Pérez",
    "Fernando Torres Alba",  "Isabel Romero Díaz",     "Javier Moreno Castro",
    "Laura Jiménez Vega",    "Miguel Hernández Gil",   "Natalia Flores Reyes",
    "Pablo Navarro Serrano",
]

# Lista de (nombre_es, nombre_en) para cada curso
CURSOS = [
    ("Álgebra Lineal",                    "Linear Algebra"),
    ("Cálculo Diferencial",               "Differential Calculus"),
    ("Bases de Datos Avanzadas",          "Advanced Databases"),
    ("Estructuras de Datos",              "Data Structures"),
    ("Sistemas Operativos",               "Operating Systems"),
    ("Redes de Computadores",             "Computer Networks"),
    ("Inteligencia Artificial",           "Artificial Intelligence"),
    ("Programación Funcional",            "Functional Programming"),
    ("Arquitectura de Software",          "Software Architecture"),
    ("Seguridad Informática",             "Computer Security"),
    ("Computación en la Nube",            "Cloud Computing"),
    ("Machine Learning",                  "Machine Learning"),
    ("Diseño de Interfaces",              "Interface Design"),
    ("Ingeniería de Software",            "Software Engineering"),
    ("Matemáticas Discretas",             "Discrete Mathematics"),
    ("Compiladores",                      "Compilers"),
    ("Visión por Computador",             "Computer Vision"),
    ("Criptografía",                      "Cryptography"),
    ("Procesamiento de Lenguaje Natural", "Natural Language Processing"),
    ("Robótica",                          "Robotics"),
]

# Compatibilidad: lista de nombres en español (usada en referencias antiguas)
CURSOS_NOMBRES = [nombre for nombre, _ in CURSOS]

# Usuarios SQLite

USUARIOS = [
    {
        "username":  "admin",
        "email":     "admin@academico.es",
        "password":  "Admin1234!",
        "nombre":    "Administrador del Sistema",
        "rol":       "admin",
        "is_active": 1,
    },
    {
        "username":  "profesor",
        "email":     "profesor@academico.es",
        "password":  "Profesor1234!",
        "nombre":    "Profesor Demo",
        "rol":       "profesor",
        "is_active": 1,
    },
    {
        "username":  "alumno",
        "email":     "alumno@academico.es",
        "password":  "Alumno1234!",
        "nombre":    "Alumno Demo",
        "rol":       "alumno",
        "is_active": 1,
    },
]
