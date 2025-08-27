from flask import Blueprint, redirect, request, session, url_for
from config import Config

bp = Blueprint('language', __name__)

@bp.route('/set-language/<language>')
def set_language(language=None):
    if language and language in Config.LANGUAGES:
        session['language'] = language
        session.permanent = True
    
    # Redirigir de vuelta a la página anterior o al home
    return redirect(request.referrer or url_for('main.home'))