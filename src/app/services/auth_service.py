from typing import Optional, Dict
import requests
from flask import current_app, session
from config import Config

class AuthService:
    """Servicio para manejar autenticación"""
    
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[Dict]:
        """Autentica al usuario contra la API de Keycloak"""
        try:
            response = requests.post(
                f"{Config.API_BASE_URL}/auth/login",
                json={
                    'username': username,
                    'password': password
                },
                timeout=10
            )
            
            print(f"Auth URL: {Config.API_BASE_URL}/auth/login")
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.content}")
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token') or data.get('token')
                user_info = data.get('user', {})
                
                if token:
                    # Guardar token en sesión para uso posterior
                    session['access_token'] = token
                    session['user_data'] = user_info
                    
                    return {
                        'token': token,
                        'user_data': user_info,
                        'username': username
                    }
            
            return None
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error connecting to auth API: {e}")
            return None
        except Exception as e:
            current_app.logger.error(f"Authentication error: {e}")
            return None
    
    @staticmethod
    def validate_token(token: str) -> bool:
        """Valida que el token siga siendo válido"""
        try:
            if not token:
                return False
            
            response = requests.get(
                f"{Config.API_BASE_URL}/auth/token/validate",
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            
            return response.status_code == 200
            
        except requests.exceptions.RequestException:
            return False
    
    @staticmethod
    def logout(token: str) -> bool:
        """Realizar logout en la API"""
        try:
            response = requests.post(
                f"{Config.API_BASE_URL}/auth/logout",
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            
            return response.status_code == 200
            
        except requests.exceptions.RequestException:
            return False
    
    @staticmethod
    def get_auth_headers(token: str = None) -> Dict[str, str]:
        """Retorna headers de autenticación para peticiones a la API"""
        if not token:
            token = session.get('access_token')
        
        if token:
            return {'Authorization': f'Bearer {token}'}
        return {}