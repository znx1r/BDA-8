import uuid
import re
from flask import Blueprint, request, render_template, jsonify, abort, session
from models import OperacionesAlumno, OperacionesAuditoria
from models import Alumnos
from ._helpers import _str, _float, paginate

alumnos_bp = Blueprint('students', __name__, url_prefix="/alumnos")

_EMAIL_RE = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')


@alumnos_bp.route('/')
def home():
    q         = _str('q')
    saldo_min = _float('saldo_min')
    saldo_max = _float('saldo_max')

    gestor   = OperacionesAlumno()
    filtered = gestor.count_filtered(q=q, saldo_min=saldo_min, saldo_max=saldo_max)
    total    = gestor.get_count()
    pg       = paginate(filtered)

    rows = gestor.get_filtered(
        q=q, saldo_min=saldo_min, saldo_max=saldo_max,
        limit=pg['limit'], offset=pg['offset'],
    )

    return render_template(
        "alumnos/list.html",
        title="Alumnos",
        rows=rows, total=total, filtered=filtered,
        q=q or '', saldo_min=saldo_min, saldo_max=saldo_max,
        **pg,
    )


@alumnos_bp.route('/<alumno_id>')
def detail(alumno_id):
    gestor = OperacionesAlumno()
    alumno = gestor.get_by_id(alumno_id)
    if not alumno:
        abort(404)
    cursos = gestor.get_cursos_by_alumno(alumno_id)
    profesores_distintos = len({c[2] for c in cursos})
    return render_template(
        "alumnos/detail.html",
        title=alumno[1],
        alumno=alumno,
        cursos=cursos,
        profesores_distintos=profesores_distintos,
    )


@alumnos_bp.route('/delete/<alumno_id>', methods=['POST'])
def delete(alumno_id):
    try:
        alumno = OperacionesAlumno().get_by_id(alumno_id)
        nombre = alumno[1] if alumno else alumno_id
        OperacionesAlumno().delete_by_id(alumno_id)
        usuario = session.get('user', {}).get('username', 'anónimo')
        OperacionesAuditoria().registrar(usuario, 'DELETE', 'alumno', alumno_id, f'Eliminado: {nombre}')
        return jsonify(ok=True, message='Alumno eliminado correctamente.')
    except Exception as e:
        return jsonify(ok=False, error=str(e))


@alumnos_bp.route('/new', methods=['POST'])
def new():
    nombre = request.form.get('nombre', '').strip()
    email  = request.form.get('email', '').strip()
    try:
        saldo = float(request.form.get('saldo', '500') or '500')
    except ValueError:
        saldo = 500.0

    if not nombre:
        return jsonify(ok=False, field='nombre', error='El nombre es obligatorio.')
    if not email:
        return jsonify(ok=False, field='email', error='El email es obligatorio.')
    if not _EMAIL_RE.match(email):
        return jsonify(ok=False, field='email', error='Formato de email no válido.')
    if saldo < 0:
        return jsonify(ok=False, field='saldo', error='El saldo no puede ser negativo.')

    try:
        alumno = Alumnos(id=str(uuid.uuid4()), nombre=nombre, email=email, saldo=saldo)
        OperacionesAlumno().insert_one_student(alumno=alumno)
        usuario = session.get('user', {}).get('username', 'anónimo')
        OperacionesAuditoria().registrar(usuario, 'CREATE', 'alumno', alumno.id, f'Creado: {nombre} ({email})')
        return jsonify(ok=True, message=f'Alumno "{nombre}" creado correctamente.')
    except Exception as e:
        err = str(e)
        if 'email' in err.lower() or 'unique' in err.lower():
            return jsonify(ok=False, field='email', error='Este email ya está registrado.')
        return jsonify(ok=False, error=err)


@alumnos_bp.route('/recharge', methods=['POST'])
def recharge():
    alumno_id = request.form.get('alumno_id', '').strip()
    try:
        cantidad = float(request.form.get('cantidad', '0') or '0')
    except ValueError:
        return jsonify(ok=False, error='Cantidad inválida.')

    if not alumno_id:
        return jsonify(ok=False, error='Falta alumno_id.')
    if cantidad <= 0:
        return jsonify(ok=False, error='La cantidad debe ser mayor que 0.')
    if cantidad > 9999:
        return jsonify(ok=False, error='Cantidad máxima: 9999 €.')

    try:
        OperacionesAlumno().recharge_saldo(alumno_id, cantidad)
        alumno = OperacionesAlumno().get_by_id(alumno_id)
        nuevo_saldo = float(alumno[4]) if alumno else None
        usuario = session.get('user', {}).get('username', 'anónimo')
        OperacionesAuditoria().registrar(usuario, 'UPDATE', 'alumno', alumno_id,
                                          f'Recarga de saldo: +{cantidad:.2f} €')
        return jsonify(ok=True, message=f'Saldo recargado: +{cantidad:.2f} €', saldo=nuevo_saldo)
    except Exception as e:
        return jsonify(ok=False, error=str(e))
