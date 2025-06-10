from functools import wraps
from flask import session, redirect, url_for, flash
from flask_login import current_user, logout_user
from flask_babel import _

def token_required(f):
    """Decorador que valida autenticación y token válido"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Primero verificar si está autenticado (equivalente a @login_required)
        if not current_user.is_authenticated:
            flash(_('Please log in to access this page.'), 'info')
            return redirect(url_for('main.login'))
        
        # Luego validar que el token siga siendo válido
        if not current_user.validate_token():
            logout_user()
            session.pop('access_token', None)
            session.pop('user_data', None)
            flash(_('Session expired. Please login again.'), 'warning')
            return redirect(url_for('main.login'))
            
        return f(*args, **kwargs)
    return decorated_function

def login_required_only(f):
    """Decorador solo para verificar login sin validar token (para casos especiales)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash(_('Please log in to access this page.'), 'info')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function