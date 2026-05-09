from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for
from models import OperacionesAuditoria
from ._helpers import _str, _date, paginate

auditoria_bp = Blueprint('auditoria', __name__, url_prefix="/auditoria")


@auditoria_bp.route('/')
def home():
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))

    q           = _str('q')
    accion      = _str('accion')
    entidad     = _str('entidad')
    fecha_desde = _date('fecha_desde')
    fecha_hasta = _date('fecha_hasta')

    gestor   = OperacionesAuditoria()
    filtered = gestor.count_filtered(q=q, accion=accion, entidad=entidad,
                                      fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
    total    = gestor.get_count()
    pg       = paginate(filtered)

    rows = gestor.get_filtered(
        q=q, accion=accion, entidad=entidad,
        fecha_desde=fecha_desde, fecha_hasta=fecha_hasta,
        limit=pg['limit'], offset=pg['offset'],
    )

    return render_template(
        "auditoria/list.html",
        title="Auditoría",
        rows=rows, total=total, filtered=filtered,
        q=q or '', accion=accion or '', entidad=entidad or '',
        fecha_desde=fecha_desde or '', fecha_hasta=fecha_hasta or '',
        is_admin=(user.get('rol') == 'admin'),
        **pg,
    )


@auditoria_bp.route('/delete/<int:audit_id>', methods=['POST'])
def delete(audit_id):
    user = session.get('user')
    if not user or user.get('rol') != 'admin':
        return jsonify(ok=False, error='Acceso denegado. Solo administradores.')
    try:
        OperacionesAuditoria().delete_by_id(audit_id)
        return jsonify(ok=True, message='Registro eliminado correctamente.')
    except Exception as e:
        return jsonify(ok=False, error=str(e))


@auditoria_bp.route('/delete-all', methods=['POST'])
def delete_all():
    user = session.get('user')
    if not user or user.get('rol') != 'admin':
        return jsonify(ok=False, error='Acceso denegado. Solo administradores.')
    try:
        OperacionesAuditoria().delete_all()
        return jsonify(ok=True, message='Historial de auditoría limpiado correctamente.')
    except Exception as e:
        return jsonify(ok=False, error=str(e))
