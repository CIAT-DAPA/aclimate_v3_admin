from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from app.models import User
from app.services.oauth_service import OAuthService
from app import login_manager
from app.decorators import token_required
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    """Carga el usuario desde la sesión"""
    return User.get(user_id)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return redirect(url_for('main.login'))

@bp.route('/login')
def login():
    """Redirigir a Keycloak para autenticación"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    try:
        # Obtener servicio OAuth desde la app
        oauth_service = current_app.extensions.get('oauth_service')
        
        if not oauth_service:
            logger.error("OAuth service not found in app extensions")
            flash(_('Authentication service not available'), 'error')
            return render_template('login.html', form=None)
        
        # Redirigir a Keycloak
        redirect_uri = url_for('main.auth_callback', _external=True)
        logger.info(f"Initiating OAuth flow with redirect URI: {redirect_uri}")
        
        return oauth_service.get_authorization_url(redirect_uri)
        
    except Exception as e:
        logger.error(f"Error in login route: {e}")
        flash(_('Error initiating authentication'), 'error')
        return render_template('login.html', form=None)

@bp.route('/auth/callback')
def auth_callback():
    """Callback de Keycloak después de autenticación"""
    try:
        # Obtener servicio OAuth
        oauth_service = current_app.extensions.get('oauth_service')
        
        if not oauth_service:
            logger.error("OAuth service not found in app extensions")
            flash(_('Authentication service not available'), 'error')
            return redirect(url_for('main.login'))
        
        # Intercambiar código por token
        token_data = oauth_service.exchange_code_for_token()
        
        if not token_data:
            logger.error("Failed to exchange code for token")
            flash(_('Authentication failed'), 'error')
            return redirect(url_for('main.login'))
        
        # Obtener información del usuario
        user_info = oauth_service.get_user_info(token_data)
        
        if not user_info:
            logger.error("Failed to get user information")
            flash(_('Failed to get user information'), 'error')
            return redirect(url_for('main.login'))
        
        # Autenticar usuario
        user = User.authenticate_oauth(token_data, user_info)
        
        if user:
            login_user(user)
            logger.info(f"User {user.username} logged in successfully")
            flash(_('Login successful!'), 'success')
            return redirect(url_for('main.home'))
        else:
            logger.error("Failed to authenticate user")
            flash(_('Authentication failed'), 'error')
            return redirect(url_for('main.login'))
            
    except Exception as e:
        logger.error(f"Auth callback error: {e}")
        flash(_('Authentication error occurred'), 'error')
        return redirect(url_for('main.login'))

@bp.route('/logout')
@token_required
def logout():
    """Logout del usuario y redirigir a Keycloak logout"""
    try:
        # Obtener servicio OAuth
        oauth_service = current_app.extensions.get('oauth_service')

        # Obtener id_token de la sesión antes de limpiarla
        id_token = session.get('id_token')
        
        # Limpiar sesión local
        session.clear()
        logout_user()
        
        if oauth_service:
            # Redirigir a logout de Keycloak
            post_logout_redirect = url_for('main.index', _external=True)
            keycloak_logout_url = oauth_service.logout_url(
                redirect_uri=post_logout_redirect,
                id_token=id_token
            )
            return redirect(keycloak_logout_url)
        else:
            flash(_('Logged out successfully'), 'info')
            return redirect(url_for('main.index'))
            
    except Exception as e:
        logger.error(f"Logout error: {e}")
        flash(_('Logout completed'), 'info')
        return redirect(url_for('main.index'))

@bp.route('/home')
@token_required
def home():
    return render_template('home.html')