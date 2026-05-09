import uuid
from flask import Blueprint, request, render_template, jsonify, abort, session
from models import OperacionesCurso, OperacionesProfesor, OperacionesAuditoria
from models import Cursos
from ._helpers import _str, _float, _int, paginate

asignaturas_bp = Blueprint('asignaturas', __name__, url_prefix="/asignaturas")


@asignaturas_bp.route('/')
def home():
    q          = _str('q')
    precio_min = _float('precio_min')
    precio_max = _float('precio_max')
    max_min    = _int('max_min')
    max_max    = _int('max_max')

    gestor   = OperacionesCurso()
    filtered = gestor.count_filtered(q=q, precio_min=precio_min, precio_max=precio_max,
                                      max_min=max_min, max_max=max_max)
    total      = gestor.get_count()
    pg         = paginate(filtered)
    profesores = OperacionesProfesor().get_all_teachers()

    rows = gestor.get_filtered(
        q=q, precio_min=precio_min, precio_max=precio_max,
        max_min=max_min, max_max=max_max,
        limit=pg['limit'], offset=pg['offset'],
    )

    return render_template(
        "asignaturas/list.html",
        title="Asignaturas",
        rows=rows, total=total, filtered=filtered, profesores=profesores,
        q=q or '', precio_min=precio_min, precio_max=precio_max,
        max_min=max_min, max_max=max_max,
        **pg,
    )


@asignaturas_bp.route('/<curso_id>')
def detail(curso_id):
    gestor = OperacionesCurso()
    curso  = gestor.get_by_id(curso_id)
    if not curso:
        abort(404)
    alumnos = gestor.get_alumnos_by_curso(curso_id)
    return render_template(
        "asignaturas/detail.html",
        title=curso[1],
        curso=curso,
        alumnos=alumnos,
    )


@asignaturas_bp.route('/new', methods=['POST'])
def new():
    nombre      = request.form.get('nombre', '').strip()
    profesor_id = request.form.get('profesor_id', '').strip()
    try:
        precio      = float(request.form.get('precio', '100') or '100')
        max_alumnos = int(request.form.get('max_alumnos', '30') or '30')
    except ValueError:
        return jsonify(ok=False, error='Precio o capacidad inválidos.')

    nombre_en   = request.form.get('nombre_en', '').strip()

    if not nombre:
        return jsonify(ok=False, field='nombre', error='El nombre es obligatorio.')
    if not profesor_id:
        return jsonify(ok=False, field='profesor_id', error='Selecciona un profesor.')
    if precio < 0:
        return jsonify(ok=False, field='precio', error='El precio no puede ser negativo.')
    if max_alumnos < 1:
        return jsonify(ok=False, field='max_alumnos', error='La capacidad mínima es 1.')

    try:
        curso = Cursos(id=str(uuid.uuid4()), nombre=nombre, nombre_en=nombre_en,
                       profesor_id=profesor_id, precio=precio, max_alumnos=max_alumnos)
        OperacionesCurso().insert_one_course(curso=curso)
        usuario = session.get('user', {}).get('username', 'anónimo')
        OperacionesAuditoria().registrar(usuario, 'CREATE', 'asignatura', curso.id, f'Creada: {nombre}')
        return jsonify(ok=True, message=f'Asignatura "{nombre}" creada correctamente.')
    except Exception as e:
        return jsonify(ok=False, error=str(e))


@asignaturas_bp.route('/update/<curso_id>', methods=['POST'])
def update(curso_id):
    nombre_en = request.form.get('nombre_en', '').strip()
    try:
        precio      = float(request.form.get('precio', '100') or '100')
        max_alumnos = int(request.form.get('max_alumnos', '30') or '30')
    except ValueError:
        return jsonify(ok=False, error='Precio o capacidad inválidos.')

    if precio < 0:
        return jsonify(ok=False, error='El precio no puede ser negativo.')
    if max_alumnos < 1:
        return jsonify(ok=False, error='La capacidad mínima es 1.')

    try:
        OperacionesCurso().update_settings(curso_id, precio, max_alumnos, nombre_en)
        usuario = session.get('user', {}).get('username', 'anónimo')
        OperacionesAuditoria().registrar(usuario, 'UPDATE', 'asignatura', curso_id,
                                          f'Actualizada: precio={precio:.2f}€, max_alumnos={max_alumnos}')
        return jsonify(ok=True, message='Asignatura actualizada correctamente.')
    except Exception as e:
        return jsonify(ok=False, error=str(e))


@asignaturas_bp.route('/delete/<curso_id>', methods=['POST'])
def delete(curso_id):
    try:
        curso = OperacionesCurso().get_by_id(curso_id)
        nombre = curso[1] if curso else curso_id
        OperacionesCurso().delete_by_id(curso_id)
        usuario = session.get('user', {}).get('username', 'anónimo')
        OperacionesAuditoria().registrar(usuario, 'DELETE', 'asignatura', curso_id, f'Eliminada: {nombre}')
        return jsonify(ok=True, message='Asignatura eliminada correctamente.')
    except Exception as e:
        return jsonify(ok=False, error=str(e))
