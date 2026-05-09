import uuid
import datetime
from flask import Blueprint, request, render_template, jsonify
from models import OperacionesMatricula, OperacionesAlumno, OperacionesCurso
from models import Matriculas
from ._helpers import _str, _date, paginate

matriculas_bp = Blueprint('matriculas', __name__, url_prefix="/matriculas")


@matriculas_bp.route('/')
def home():
    q           = _str('q')
    fecha_desde = _date('fecha_desde')
    fecha_hasta = _date('fecha_hasta')

    gestor   = OperacionesMatricula()
    filtered = gestor.count_filtered(q=q, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
    total    = gestor.get_count()
    pg       = paginate(filtered)

    rows    = gestor.get_filtered(q=q, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta,
                                   limit=pg['limit'], offset=pg['offset'])
    alumnos = OperacionesAlumno().get_all_students()
    cursos  = OperacionesCurso().get_all_courses()

    return render_template(
        "matriculas/list.html",
        title="Matrículas",
        rows=rows, total=total, filtered=filtered,
        q=q or '', fecha_desde=fecha_desde or '', fecha_hasta=fecha_hasta or '',
        alumnos=alumnos, cursos=cursos,
        **pg,
    )


@matriculas_bp.route('/delete', methods=['POST'])
def delete():
    alumno_id = request.form.get('alumno_id', '').strip()
    curso_id  = request.form.get('curso_id', '').strip()
    if not alumno_id or not curso_id:
        return jsonify(ok=False, error='Faltan parámetros.')
    try:
        OperacionesMatricula().delete_enrollment(alumno_id, curso_id)
        return jsonify(ok=True, message='Matrícula eliminada correctamente.')
    except Exception as e:
        return jsonify(ok=False, error=str(e))


@matriculas_bp.route('/new', methods=['POST'])
def new():
    alumno_id = request.form.get('alumno_id', '').strip()
    curso_id  = request.form.get('curso_id', '').strip()

    if not alumno_id:
        return jsonify(ok=False, field='alumno_id', error='Selecciona un alumno.')
    if not curso_id:
        return jsonify(ok=False, field='curso_id', error='Selecciona un curso.')

    gestor = OperacionesMatricula()
    if gestor.check_exists(alumno_id, curso_id):
        return jsonify(ok=False, field='curso_id', error='El alumno ya está matriculado en ese curso (PRIMARY KEY).')

    try:
        matricula = Matriculas(
            alumno_id=alumno_id,
            curso_id=curso_id,
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )
        gestor.insert_one_enrollment(matricula=matricula)
        return jsonify(ok=True, message='Matrícula registrada correctamente.')
    except Exception as e:
        return jsonify(ok=False, error=str(e))


@matriculas_bp.route('/enroll', methods=['POST'])
def enroll():
    """Proceso de matriculación transaccional con log visual de pasos."""
    alumno_id = request.form.get('alumno_id', '').strip()
    curso_id  = request.form.get('curso_id', '').strip()

    if not alumno_id:
        return jsonify(ok=False, error='Selecciona un alumno.')
    if not curso_id:
        return jsonify(ok=False, error='Selecciona una asignatura.')

    from flask import session
    usuario = session.get('user', {}).get('username', 'anónimo')
    result = OperacionesMatricula().matricular_transaccional(alumno_id, curso_id, usuario)
    return jsonify(result)
