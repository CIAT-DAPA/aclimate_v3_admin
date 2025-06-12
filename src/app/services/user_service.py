from typing import List, Dict, Optional
from datetime import datetime
import requests
from flask import current_app, session
from config import Config

class UserService:
    """Servicio para manejar usuarios con API real"""
    
    def __init__(self):
        # Datos simulados como fallback
        self._fallback_users = [
            {
                'id': 1,
                'username': 'admin',
                'email': 'admin@aclimate.org',
                'role_id': 1,
                'role_name': 'Admin',
                'enabled': True,
                'email_verified': True,
                'created_timestamp': int(datetime.now().timestamp() * 1000),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
        ]
        self._next_id = 2
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Obtener headers de autenticación"""
        token = session.get('access_token')
        if token:
            return {'Authorization': f'Bearer {token}'}
        return {}
    
    def get_all(self) -> List[Dict]:
        """Obtener todos los usuarios desde la API"""
        try:
            response = requests.get(
                f"{Config.API_BASE_URL}/users/get-users",
                headers=self._get_auth_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('users', [])
            else:
                current_app.logger.error(f"Error fetching users from API: {response.status_code}")
                return self._fallback_users.copy()
                
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error connecting to users API: {e}")
            return self._fallback_users.copy()
    
    def get_active_users(self) -> List[Dict]:
        """Obtener solo los usuarios activos"""
        all_users = self.get_all()
        return [user for user in all_users if user.get('enabled', True)]
    
    def get_by_id(self, user_id: int) -> Optional[Dict]:
        """Obtener usuario por ID desde la API"""
        try:
            response = requests.get(
                f"{Config.API_BASE_URL}/users/get-users/{user_id}",
                headers=self._get_auth_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                # Fallback a datos simulados
                for user in self._fallback_users:
                    if user['id'] == user_id:
                        return user.copy()
                return None
                
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error fetching user from API: {e}")
            # Fallback a datos simulados
            for user in self._fallback_users:
                if user['id'] == user_id:
                    return user.copy()
            return None
    
    def get_by_username(self, username: str) -> Optional[Dict]:
        """Obtener usuario por nombre de usuario"""
        all_users = self.get_all()
        for user in all_users:
            if user['username'].lower() == username.lower():
                return user
        return None
    
    def get_by_email(self, email: str) -> Optional[Dict]:
        """Obtener usuario por email"""
        all_users = self.get_all()
        for user in all_users:
            if user['email'].lower() == email.lower():
                return user
        return None

    def create(self, username: str, email: str, name: str, last_name: str, password: str) -> Dict:
        """Crear nuevo usuario en la API"""
        try:
            response = requests.post(
                f"{Config.API_BASE_URL}/users/create-user",
                headers=self._get_auth_headers(),
                json={
                    "username": username,
                    "email": email,
                    "firstName": name,
                    "lastName": last_name,
                    "emailVerified": False,
                    "enabled": True,
                    "attributes": {},
                    "credentials": [
                        {
                        "type": "password",
                        "value": password,
                        "temporary": False
                        }
                    ]
                },
                timeout=10
            )
            
            if response.status_code == 201:
                return response.json()
            elif response.status_code == 400:
                error_data = response.json()
                raise ValueError(error_data.get('message', 'Error creating user'))
            else:
                raise Exception(f"Error creating user: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error creating user in API: {e}")
            # Fallback: crear en memoria como antes
            return self._create_fallback(username, email, name, last_name, password)
        except ValueError:
            raise  # Re-raise validation errors
        except Exception as e:
            current_app.logger.error(f"Unexpected error creating user: {e}")
            raise
    
    def update(self, user_id: int, username: str = None, email: str = None, role_id: int = None, role_name: str = None) -> Optional[Dict]:
        """Actualizar usuario existente en la API"""
        try:
            update_data = {}
            if username is not None:
                update_data['username'] = username
            if email is not None:
                update_data['email'] = email
            if role_id is not None:
                update_data['role_id'] = role_id
            
            response = requests.put(
                f"{Config.API_BASE_URL}/users/update-user/{user_id}",
                headers=self._get_auth_headers(),
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                error_data = response.json()
                raise ValueError(error_data.get('message', 'Error updating user'))
            else:
                return None
                
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error updating user in API: {e}")
            return None
        except ValueError:
            raise  # Re-raise validation errors
    
    def delete(self, user_id: int) -> bool:
        """Eliminar (deshabilitar) usuario en la API"""
        try:
            response = requests.delete(
                f"{Config.API_BASE_URL}/users/delete-user/{user_id}",
                headers=self._get_auth_headers(),
                timeout=10
            )
            
            return response.status_code == 200
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error deleting user in API: {e}")
            return False
    
    def assign_role(self, user_id: int, role_id: int) -> bool:
        """Asignar rol a usuario en la API"""
        try:
            response = requests.post(
                f"{Config.API_BASE_URL}/users/assign-role",
                headers=self._get_auth_headers(),
                json={
                    'user_id': user_id,
                    'role_id': role_id
                },
                timeout=10
            )
            
            return response.status_code == 200
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error assigning role in API: {e}")
            return False
    
    def restore(self, user_id: int) -> bool:
        """Restaurar usuario deshabilitado"""
        try:
            response = requests.post(
                f"{Config.API_BASE_URL}/users/restore-user/{user_id}",
                headers=self._get_auth_headers(),
                timeout=10
            )
            
            return response.status_code == 200
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error restoring user in API: {e}")
            return False
    
    def search_users(self, query: str) -> List[Dict]:
        """Buscar usuarios por username o email"""
        all_users = self.get_all()
        query_lower = query.lower()
        results = []
        
        for user in all_users:
            if user.get('enabled', True):
                if (query_lower in user.get('username', '').lower() or 
                    query_lower in user.get('email', '').lower()):
                    results.append(user)
        
        return results
    
    def get_users_by_role(self, role_id: int) -> List[Dict]:
        """Obtener usuarios por rol"""
        all_users = self.get_all()
        return [user for user in all_users if user['role_id'] == role_id and user.get('enabled', True)]
    
    def get_user_count(self) -> Dict[str, int]:
        """Obtener estadísticas de usuarios"""
        all_users = self.get_all()
        total = len(all_users)
        active = len([u for u in all_users if u.get('enabled', True)])
        inactive = total - active
        verified = len([u for u in all_users if u.get('email_verified', False)])
        
        return {
            'total': total,
            'active': active,
            'inactive': inactive,
            'verified': verified,
            'unverified': total - verified
        }
    
    def _create_fallback(self, username: str, email: str, role_id: int, role_name: str) -> Dict:
        """Crear usuario en fallback (memoria) cuando API no esté disponible"""
        # Verificar duplicados en fallback
        if any(u['username'].lower() == username.lower() for u in self._fallback_users):
            raise ValueError(f"Ya existe un usuario con el nombre '{username}'")
        
        if any(u['email'].lower() == email.lower() for u in self._fallback_users):
            raise ValueError(f"Ya existe un usuario con el email '{email}'")
        
        new_user = {
            'id': self._next_id,
            'username': username,
            'email': email,
            'role_id': role_id,
            'role_name': role_name,
            'enabled': True,
            'email_verified': False,
            'created_timestamp': int(datetime.now().timestamp() * 1000),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        self._fallback_users.append(new_user)
        self._next_id += 1
        
        return new_user.copy()