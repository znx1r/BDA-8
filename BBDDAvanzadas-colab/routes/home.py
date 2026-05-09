from flask import (
    Blueprint, request, render_template
)
from models import OperacionesAlumno, OperacionesCurso, OperacionesMatricula, OperacionesProfesor

home_bp = Blueprint('home', __name__, url_prefix="/home")

@home_bp.route('/')
def home():
    title = "Inicio"
    count_alumnos = OperacionesAlumno().get_count() 
    count_profesores = OperacionesProfesor().get_count()
    count_curso = OperacionesCurso().get_count()
    count_matricula = OperacionesMatricula().get_count()

    print(count_alumnos, count_profesores, count_curso, count_matricula)
    return render_template(
        "/home/home.html", 
        title = title, 
        n_alumnos = count_alumnos, 
        n_profesores = count_profesores,
        n_cursos = count_curso,
        n_matriculas = count_matricula
    )
