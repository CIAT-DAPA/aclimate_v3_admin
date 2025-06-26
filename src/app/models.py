from flask_login import UserMixin
from flask import session
import logging

logger = logging.getLogger(__name__)

class User(UserMixin):
    def __init__(self, user_data):
        # Log para debug
        logger.debug(f"Creating user with data: {user_data}")
        
        # Keycloak puede devolver diferentes campos según la configuración
        self.id = (user_data.get('sub') or 
                  user_data.get('id') or 
                  user_data.get('preferred_username') or 
                  user_data.get('username'))
        self.username = (user_data.get('preferred_username') or 
                         user_data.get('username') or 
                         user_data.get('email', '').split('@')[0])
        self.email = user_data.get('email', '')
        self.first_name = user_data.get('given_name', '')
        self.last_name = user_data.get('family_name', '')
        self.name = user_data.get('name', f"{self.first_name} {self.last_name}".strip())
        
        # Roles pueden venir en diferentes lugares
        self.roles = (user_data.get('roles', []) or 
                     user_data.get('realm_access', {}).get('roles', []) or
                     user_data.get('resource_access', {}).get('roles', []))
        
        logger.info(f"Created user: {self.username} (ID: {self.id})")
        
    def get_id(self):
        return str(self.id)
    
    @staticmethod
    def get(user_id):
        """Cargar usuario desde la sesión"""
        user_data = session.get('user_data')
        if user_data:
            user = User(user_data)
            if str(user.id) == str(user_id):
                return user
        return None
    
    @staticmethod
    def authenticate_oauth(token_data, user_info):
        """Autenticar usuario con datos OAuth"""
        if token_data and user_info:
            # Guardar datos en sesión
            session['access_token'] = token_data.get('access_token')
            session['refresh_token'] = token_data.get('refresh_token')
            session['id_token'] = token_data.get('id_token')
            session['user_data'] = user_info
            
            logger.info(f"Authenticated user via OAuth: {user_info.get('preferred_username', 'unknown')}")
            logger.debug(f"Stored tokens: access_token={bool(token_data.get('access_token'))}, id_token={bool(token_data.get('id_token'))}")
            return User(user_info)
        return None
    
    def validate_token(self):
        """Validar que el token del usuario siga siendo válido"""
        access_token = session.get('access_token')
        if not access_token:
            logger.warning("No access token found in session")
            return False
        
        from app.services.oauth_service import OAuthService
        oauth_service = OAuthService()
        is_valid = oauth_service.validate_token(access_token)
        
        if not is_valid:
            logger.warning(f"Token validation failed for user: {self.username}")
        
        return is_valid