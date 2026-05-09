from flask import Blueprint, render_template, jsonify
from models.db.transacciones import demo_fk_violation, demo_pk_duplicate, demo_commit_exitoso

transacciones_bp = Blueprint('transacciones', __name__, url_prefix="/transacciones")

_DEMOS = {
    "fk-violation":   demo_fk_violation,
    "pk-duplicate":   demo_pk_duplicate,
    "commit-exitoso": demo_commit_exitoso,
}


@transacciones_bp.route('/')
def home():
    return render_template("transacciones/index.html", title="Transacciones")


@transacciones_bp.route('/run/<demo_id>', methods=['POST'])
def run(demo_id):
    fn = _DEMOS.get(demo_id)
    if not fn:
        return jsonify(ok=False, error=f"Demo '{demo_id}' no existe."), 404
    try:
        steps = fn()
        return jsonify(ok=True, steps=steps)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500
