from flask import Blueprint, request, render_template
from models import OperacionesVista
from ._helpers import _str, _date, paginate

vista_bp = Blueprint('vista', __name__, url_prefix="/vista")


@vista_bp.route('/')
def home():
    q           = _str('q')
    fecha_desde = _date('fecha_desde')
    fecha_hasta = _date('fecha_hasta')

    gestor   = OperacionesVista()
    filtered = gestor.count_filtered(q=q, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
    total    = gestor.get_count()
    pg       = paginate(filtered)

    rows = gestor.get_filtered(
        q=q, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta,
        limit=pg['limit'], offset=pg['offset'],
    )

    return render_template(
        "vista/list.html",
        title="Vista: Matrículas",
        rows=rows, total=total, filtered=filtered,
        q=q or '', fecha_desde=fecha_desde or '', fecha_hasta=fecha_hasta or '',
        **pg,
    )
