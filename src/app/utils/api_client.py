import requests
from flask import current_app, session
from flask_login import current_user
from config import Config

class APIClient:
    """Cliente para hacer peticiones autenticadas a la API"""
    
    def __init__(self):
        self.base_url = Config.API_BASE_URL
    
    def _get_headers(self):
        """Obtiene headers de autenticación"""
        headers = {'Content-Type': 'application/json'}
        
        if current_user.is_authenticated and current_user.token:
            headers['Authorization'] = f'Bearer {current_user.token}'
        elif 'access_token' in session:
            headers['Authorization'] = f'Bearer {session["access_token"]}'
            
        return headers
    
    def get(self, endpoint, params=None):
        """Petición GET autenticada"""
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self._get_headers(),
                params=params,
                timeout=10
            )
            return response
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"API GET error: {e}")
            return None
    
    def post(self, endpoint, data=None):
        """Petición POST autenticada"""
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                headers=self._get_headers(),
                json=data,
                timeout=10
            )
            return response
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"API POST error: {e}")
            return None
    
    def put(self, endpoint, data=None):
        """Petición PUT autenticada"""
        try:
            response = requests.put(
                f"{self.base_url}{endpoint}",
                headers=self._get_headers(),
                json=data,
                timeout=10
            )
            return response
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"API PUT error: {e}")
            return None
    
    def delete(self, endpoint):
        """Petición DELETE autenticada"""
        try:
            response = requests.delete(
                f"{self.base_url}{endpoint}",
                headers=self._get_headers(),
                timeout=10
            )
            return response
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"API DELETE error: {e}")
            return None

# Instancia global para usar en toda la aplicación
api_client = APIClient()