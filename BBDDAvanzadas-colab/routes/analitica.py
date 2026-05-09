from flask import Blueprint, render_template
from models import OperacionesAnalitica

analitica_bp = Blueprint('analitica', __name__, url_prefix="/analitica")


@analitica_bp.route('/')
def home():
    gestor = OperacionesAnalitica()
    return render_template(
        "analitica/index.html",
        title="Analítica SQL",
        rows_filter        = gestor.get_filter()        or [],
        rows_rollup        = gestor.get_rollup()        or [],
        rows_grouping_sets = gestor.get_grouping_sets() or [],
        rows_row_number    = gestor.get_row_number()    or [],
    )
