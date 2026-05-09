from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from models.db.sqlite import Sqlite

auth_bp = Blueprint('auth', __name__, url_prefix="/auth")


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('home.home'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        db = Sqlite()
        if not username or not password:
            error = 'Introduce usuario y contraseña.'
        elif not db.verify_password(username, password):
            error = 'Usuario o contraseña incorrectos.'
        else:
            user = db.get_user_by_username(username)
            session['user'] = {
                'username': user['username'],
                'nombre':   user['nombre'],
                'rol':      user['rol'],
            }
            next_url = request.args.get('next') or url_for('home.home')
            return redirect(next_url)

    return render_template('auth/login.html', title='Iniciar sesión', error=error)


@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('auth.login'))
