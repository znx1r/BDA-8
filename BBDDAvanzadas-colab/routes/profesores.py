import uuid
from flask import Blueprint, request, render_template, jsonify, abort, session
from models import OperacionesProfesor, OperacionesAuditoria
from models import Profesores
from ._helpers import _str, _int, paginate

profesores_bp = Blueprint('profesores', __name__, url_prefix="/profesores")


@profesores_bp.route('/')
def home():
    q          = _str('q')
    cursos_min = _int('cursos_min')
    cursos_max = _int('cursos_max')

    gestor   = OperacionesProfesor()
    filtered = gestor.count_filtered(q=q, cursos_min=cursos_min, cursos_max=cursos_max)
    total    = gestor.get_count()
    pg       = paginate(filtered)

    rows = gestor.get_filtered(
        q=q, cursos_min=cursos_min, cursos_max=cursos_max,
        limit=pg['limit'], offset=pg['offset'],
    )

    return render_template(
        "profesores/list.html",
        title="Profesores",
        rows=rows, total=total, filtered=filtered,
        q=q or '', cursos_min=cursos_min, cursos_max=cursos_max,
        **pg,
    )


@profesores_bp.route('/<profesor_id>')
def detail(profesor_id):
    gestor = OperacionesProfesor()
    profesor = gestor.get_by_id(profesor_id)
    if not profesor:
        abort(404)
    cursos = gestor.get_cursos_by_profesor(profesor_id)
    return render_template(
        "profesores/detail.html",
        title=profesor[1],
        profesor=profesor,
        cursos=cursos,
    )


@profesores_bp.route('/delete/<profesor_id>', methods=['POST'])
def delete(profesor_id):
    try:
        profesor = OperacionesProfesor().get_by_id(profesor_id)
        nombre = profesor[1] if profesor else profesor_id
        OperacionesProfesor().delete_by_id(profesor_id)
        usuario = session.get('user', {}).get('username', 'anónimo')
        OperacionesAuditoria().registrar(usuario, 'DELETE', 'profesor', profesor_id, f'Eliminado: {nombre}')
        return jsonify(ok=True, message='Profesor eliminado correctamente.')
    except Exception as e:
        return jsonify(ok=False, error=str(e))


@profesores_bp.route('/new', methods=['POST'])
def new():
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        return jsonify(ok=False, error='El nombre es obligatorio.')
    try:
        profesor = Profesores(id=str(uuid.uuid4()), nombre=nombre)
        OperacionesProfesor().insert_one_teacher(profesor=profesor)
        usuario = session.get('user', {}).get('username', 'anónimo')
        OperacionesAuditoria().registrar(usuario, 'CREATE', 'profesor', profesor.id, f'Creado: {nombre}')
        return jsonify(ok=True, message=f'Profesor "{nombre}" creado correctamente.')
    except Exception as e:
        return jsonify(ok=False, error=str(e))
