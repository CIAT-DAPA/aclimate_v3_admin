from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from app.models.User import User
from app.services.oauth_service import OAuthService
from app.services.user_service import UserService
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
        
        # Enriquecer información del usuario con roles desde la API
        user_info_enriched = enrich_user_with_roles(token_data, user_info)
        
        # Autenticar usuario con información enriquecida
        user = User.authenticate_oauth(token_data, user_info_enriched)
        
        if user:
            login_user(user)
            logger.info(f"User {user.username} logged in successfully with roles: {user.roles}")
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

def enrich_user_with_roles(token_data, user_info):
    """
    Enriquece la información del usuario con roles obtenidos de la API
    ya que Keycloak no los incluye en el token/userinfo
    """
    try:
        logger.info("Enriching user information with roles from API...")
        
        # Obtener user ID desde el user_info
        user_id = (user_info.get('sub') or 
                  user_info.get('id') or 
                  user_info.get('preferred_username'))
        
        if not user_id:
            logger.warning("Could not determine user ID for role enrichment")
            return user_info
        
        logger.info(f"Enriching roles for user ID: {user_id}")
        
        # Guardar temporalmente el token en la sesión para que el UserService pueda usarlo
        current_access_token = session.get('access_token')
        session['access_token'] = token_data.get('access_token')
        
        try:
            # Obtener información completa del usuario desde la API
            user_service = UserService()
            complete_user_data = user_service.get_by_id(user_id)
            
            logger.info(f"Retrieved complete user data from API: {complete_user_data}")
            
            # Extraer roles de diferentes fuentes en la respuesta de la API
            api_roles = []
            
            # 1. Extraer del campo 'role_name' directo
            role_name = complete_user_data.get('role_name')
            if role_name:
                api_roles.append(role_name)
                logger.info(f"Found role from 'role_name': {role_name}")
            
            # 2. Extraer de 'client_roles' array
            client_roles = complete_user_data.get('client_roles', [])
            if client_roles:
                logger.info(f"Processing client_roles: {client_roles}")
                for role in client_roles:
                    if isinstance(role, dict):
                        role_name = role.get('name')
                        if role_name and role_name not in api_roles:
                            api_roles.append(role_name)
                            logger.info(f"Found role from 'client_roles': {role_name}")
                    elif isinstance(role, str):
                        if role not in api_roles:
                            api_roles.append(role)
                            logger.info(f"Found role from 'client_roles' (string): {role}")
            
            # 3. Extraer de cualquier otro campo 'roles' si existe
            roles_array = complete_user_data.get('roles', [])
            if roles_array:
                logger.info(f"Processing roles array: {roles_array}")
                for role in roles_array:
                    if isinstance(role, str) and role not in api_roles:
                        api_roles.append(role)
                        logger.info(f"Found role from 'roles' array: {role}")
            
            logger.info(f"Final extracted roles from API: {api_roles}")
            
            # Enriquecer user_info con los roles
            enriched_user_info = user_info.copy()
            
            # Agregar roles en diferentes ubicaciones para compatibilidad
            enriched_user_info['roles'] = api_roles
            enriched_user_info['client_roles'] = client_roles
            
            # También agregar en realm_access para compatibilidad con el código existente
            if 'realm_access' not in enriched_user_info:
                enriched_user_info['realm_access'] = {}
            enriched_user_info['realm_access']['roles'] = api_roles
            
            # Agregar campos adicionales del API para mayor información
            enriched_user_info['role_name'] = complete_user_data.get('role_name')
            enriched_user_info['role_id'] = complete_user_data.get('role_id')
            
            # Agregar información adicional del usuario si está disponible
            if complete_user_data.get('first_name'):
                enriched_user_info['given_name'] = complete_user_data.get('first_name')
            if complete_user_data.get('last_name'):
                enriched_user_info['family_name'] = complete_user_data.get('last_name')
            if complete_user_data.get('email'):
                enriched_user_info['email'] = complete_user_data.get('email')
            if complete_user_data.get('username'):
                enriched_user_info['preferred_username'] = complete_user_data.get('username')
            
            logger.info(f"Successfully enriched user info with roles: {api_roles}")
            logger.info(f"Enriched user_info keys: {list(enriched_user_info.keys())}")
            
            return enriched_user_info
            
        except Exception as api_error:
            logger.error(f"Error fetching user data from API: {api_error}")
            # Si falla la llamada a la API, devolver la información original
            return user_info
            
        finally:
            # Restaurar el token anterior en la sesión
            if current_access_token is not None:
                session['access_token'] = current_access_token
            elif 'access_token' in session:
                del session['access_token']
                
    except Exception as e:
        logger.error(f"Error in role enrichment: {e}")
        return user_info

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
            flash(_('Roles refreshed successfully'), 'success')
            return jsonify({
                'message': 'Roles refreshed successfully',
                'roles': current_user.roles,
                'accessible_modules': current_user.get_accessible_modules(),
                'success': True
            })
        else:
            flash(_('Failed to refresh roles'), 'error')
            return jsonify({
                'message': 'Failed to refresh roles',
                'success': False
            }), 500
            
    except Exception as e:
        logger.error(f"Error refreshing roles: {e}")
        flash(_('Error refreshing roles'), 'error')
        return jsonify({
            'error': str(e),
            'success': False
        }), 500