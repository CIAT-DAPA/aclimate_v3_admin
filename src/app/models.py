from flask_login import UserMixin
from flask import session
from app.services.auth_service import AuthService

class User(UserMixin):
    def __init__(self, id, username, email=None, token=None, user_data=None):
        self.id = id
        self.username = username
        self.email = email
        self.token = token
        self.user_data = user_data or {}
    
    @staticmethod
    def authenticate(username, password):
        """Autentica al usuario usando AuthService"""
        auth_data = AuthService.authenticate(username, password)
        
        if auth_data:
            user_info = auth_data['user_data']
            return User(
                id=user_info.get('id', username),
                username=username,
                email=user_info.get('email'),
                token=auth_data['token'],
                user_data=user_info
            )
        
        return None
    
    @staticmethod
    def get(user_id):
        """Recupera usuario desde la sesión"""
        if 'access_token' in session and 'user_data' in session:
            user_data = session['user_data']
            return User(
                id=user_data.get('id', user_id),
                username=user_data.get('username', user_id),
                email=user_data.get('email'),
                token=session['access_token'],
                user_data=user_data
            )
        return None
    
    def validate_token(self):
        """Valida que el token siga siendo válido usando AuthService"""
        return AuthService.validate_token(self.token)
    
    @property
    def role(self):
        """Obtiene el rol del usuario desde user_data"""
        return self.user_data.get('role', 'user')
    
    def get_auth_headers(self):
        """Retorna headers de autenticación para peticiones a la API"""
        return AuthService.get_auth_headers(self.token)