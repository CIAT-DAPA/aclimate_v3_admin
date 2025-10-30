from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from app.models.User import User
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
            flash(_('Servicio de autenticación no disponible'), 'error')
            return render_template('login.html', form=None)
        
        # Redirigir a Keycloak
        redirect_uri = url_for('main.auth_callback', _external=True)
        logger.info(f"Initiating OAuth flow with redirect URI: {redirect_uri}")
        
        return oauth_service.get_authorization_url(redirect_uri)
        
    except Exception as e:
        logger.error(f"Error in login route: {e}")
        flash(_('Error al iniciar autenticación'), 'error')
        return render_template('login.html', form=None)

@bp.route('/auth/callback')
def auth_callback():
    """Callback de Keycloak después de autenticación"""
    try:
        # Obtener servicio OAuth
        oauth_service = current_app.extensions.get('oauth_service')
        
        if not oauth_service:
            logger.error("OAuth service not found in app extensions")
            flash(_('Servicio de autenticación no disponible'), 'error')
            return redirect(url_for('main.login'))
        
        # Intercambiar código por token
        token_data = oauth_service.exchange_code_for_token()
        
        if not token_data:
            logger.error("Failed to exchange code for token")
            flash(_('Falló la autenticación'), 'error')
            return redirect(url_for('main.login'))
        
        # Obtener información del usuario
        user_info = oauth_service.get_user_info(token_data)
        
        if not user_info:
            logger.error("Failed to get user information")
            flash(_('No se pudo obtener información del usuario'), 'error')
            return redirect(url_for('main.login'))
        
        # Get Keycloak user ID
        keycloak_id = user_info.get('sub')
        if not keycloak_id:
            logger.error("No 'sub' (user ID) found in Keycloak user info")
            flash(_('Información de usuario inválida'), 'error')
            return redirect(url_for('main.login'))
        
        # Autenticar usuario con información de Keycloak
        # Nota: El usuario debe existir en BD ya que se crea desde el panel admin
        user = User.authenticate_oauth(token_data, user_info)
        
        if user:
            login_user(user)
            logger.info(f"User {user.username} logged in successfully")
            flash(_('Inicio de sesión exitoso!'), 'success')
            return redirect(url_for('main.home'))
        else:
            logger.error("Failed to authenticate user")
            flash(_('Falló la autenticación'), 'error')
            return redirect(url_for('main.login'))
            
    except Exception as e:
        logger.error(f"Auth callback error: {e}")
        flash(_('Ocurrió un error de autenticación'), 'error')
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
            flash(_('Cierre de sesión exitoso'), 'info')
            return redirect(url_for('main.index'))
            
    except Exception as e:
        logger.error(f"Logout error: {e}")
        flash(_('Cierre de sesión completado'), 'info')
        return redirect(url_for('main.index'))

@bp.route('/home')
@token_required
def home():
    return render_template('home.html')

@bp.route('/debug/user-info')
@token_required
def debug_user_info():
    """Endpoint de debug para verificar información del usuario y roles"""
    try:
        user_data = {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'roles': current_user.roles,
            'accessible_modules': current_user.get_accessible_modules(),
            'is_admin': current_user.is_admin(),
            'is_super_admin': current_user.is_super_admin(),
        }
        
        session_data = {
            'user_data': session.get('user_data', {}),
            'has_access_token': bool(session.get('access_token')),
            'has_id_token': bool(session.get('id_token')),
        }
        
        return jsonify({
            'user': user_data,
            'session': session_data,
            'success': True
        })
        
    except Exception as e:
        logger.error(f"Error in debug endpoint: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@bp.route('/refresh-roles')
@token_required
def refresh_roles():
    """Endpoint para refrescar manualmente los roles del usuario"""
    try:
        success = current_user.refresh_roles()
        
        if success:
            flash(_('Roles actualizados exitosamente'), 'success')
            return jsonify({
                'message': 'Roles refreshed successfully',
                'roles': current_user.roles,
                'accessible_modules': current_user.get_accessible_modules(),
                'success': True
            })
        else:
            flash(_('No se pudieron actualizar los roles'), 'error')
            return jsonify({
                'message': 'Failed to refresh roles',
                'success': False
            }), 500
            
    except Exception as e:
        logger.error(f"Error refreshing roles: {e}")
        flash(_('Error al actualizar roles'), 'error')
        return jsonify({
            'error': str(e),
            'success': False
        }), 500