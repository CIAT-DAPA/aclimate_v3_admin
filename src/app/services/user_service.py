from typing import List, Dict, Optional
from datetime import datetime
import requests
from flask import current_app
from config import Config

class UserService:
    """Servicio para manejar usuarios - actualmente con datos simulados"""
    
    def __init__(self):
        # Simulamos una base de datos en memoria con usuarios
        self._users = [
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
            },
            {
                'id': 2,
                'username': 'geo_admin',
                'email': 'geo.admin@aclimate.org',
                'role_id': 2,
                'role_name': 'Geo Admin',
                'enabled': True,
                'email_verified': True,
                'created_timestamp': int(datetime.now().timestamp() * 1000),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            {
                'id': 3,
                'username': 'guest_user',
                'email': 'guest@aclimate.org',
                'role_id': 3,
                'role_name': 'Guest',
                'enabled': True,
                'email_verified': False,
                'created_timestamp': int(datetime.now().timestamp() * 1000),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
        ]
        self._next_id = 4
    
    def get_all(self) -> List[Dict]:
        """Obtener todos los usuarios"""
        # TODO: Cuando la API esté lista, usar:
        # return self._fetch_users_from_api()
        return self._users.copy()
    
    def get_active_users(self) -> List[Dict]:
        """Obtener solo los usuarios activos"""
        return [user.copy() for user in self._users if user.get('enabled', True)]
    
    def get_by_id(self, user_id: int) -> Optional[Dict]:
        """Obtener usuario por ID"""
        for user in self._users:
            if user['id'] == user_id:
                return user.copy()
        return None
    
    def get_by_username(self, username: str) -> Optional[Dict]:
        """Obtener usuario por nombre de usuario"""
        for user in self._users:
            if user['username'].lower() == username.lower():
                return user.copy()
        return None
    
    def get_by_email(self, email: str) -> Optional[Dict]:
        """Obtener usuario por email"""
        for user in self._users:
            if user['email'].lower() == email.lower():
                return user.copy()
        return None
    
    def create(self, username: str, email: str, role_id: int, role_name: str) -> Dict:
        """Crear nuevo usuario con solo los campos esenciales"""
        
        # Verificar si ya existe un usuario con ese username o email
        if self.get_by_username(username):
            raise ValueError(f"Ya existe un usuario con el nombre '{username}'")
        
        if self.get_by_email(email):
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
        
        # TODO: Cuando la API esté lista, usar:
        # return self._create_user_in_api(new_user)
        
        self._users.append(new_user)
        self._next_id += 1
        
        return new_user.copy()
    
    def update(self, user_id: int, username: str = None, email: str = None, role_id: int = None, role_name: str = None) -> Optional[Dict]:
        """Actualizar usuario existente"""
        for i, user in enumerate(self._users):
            if user['id'] == user_id:
                
                # Verificar duplicados si se está actualizando username o email
                if username and username != user['username']:
                    existing = self.get_by_username(username)
                    if existing and existing['id'] != user_id:
                        raise ValueError(f"Ya existe un usuario con el nombre '{username}'")
                    self._users[i]['username'] = username
                
                if email and email != user['email']:
                    existing = self.get_by_email(email)
                    if existing and existing['id'] != user_id:
                        raise ValueError(f"Ya existe un usuario con el email '{email}'")
                    self._users[i]['email'] = email
                
                if role_id is not None:
                    self._users[i]['role_id'] = role_id
                
                if role_name:
                    self._users[i]['role_name'] = role_name
                
                self._users[i]['updated_at'] = datetime.now()
                
                # TODO: Cuando la API esté lista, usar:
                # return self._update_user_in_api(user_id, self._users[i])
                
                return self._users[i].copy()
        
        return None
    
    def delete(self, user_id: int) -> bool:
        """Deshabilitar usuario (soft delete)"""
        for i, user in enumerate(self._users):
            if user['id'] == user_id:
                self._users[i]['enabled'] = False
                self._users[i]['updated_at'] = datetime.now()
                
                # TODO: Cuando la API esté lista, usar:
                # return self._disable_user_in_api(user_id)
                
                return True
        return False
    
    def restore(self, user_id: int) -> bool:
        """Restaurar usuario deshabilitado"""
        for i, user in enumerate(self._users):
            if user['id'] == user_id:
                self._users[i]['enabled'] = True
                self._users[i]['updated_at'] = datetime.now()
                return True
        return False
    
    def get_users_by_role(self, role_id: int) -> List[Dict]:
        """Obtener usuarios por rol"""
        return [user.copy() for user in self._users if user['role_id'] == role_id and user.get('enabled', True)]
    
    def search_users(self, query: str) -> List[Dict]:
        """Buscar usuarios por username o email"""
        query_lower = query.lower()
        results = []
        
        for user in self._users:
            if user.get('enabled', True):
                if (query_lower in user.get('username', '').lower() or 
                    query_lower in user.get('email', '').lower()):
                    results.append(user.copy())
        
        return results
    
    def get_user_count(self) -> Dict[str, int]:
        """Obtener estadísticas de usuarios"""
        total = len(self._users)
        active = len([u for u in self._users if u.get('enabled', True)])
        inactive = total - active
        verified = len([u for u in self._users if u.get('email_verified', False)])
        
        return {
            'total': total,
            'active': active,
            'inactive': inactive,
            'verified': verified,
            'unverified': total - verified
        }
    
    # Métodos para cuando la API esté disponible
    def _fetch_users_from_api(self) -> List[Dict]:
        """Obtener usuarios desde la API (futuro)"""
        try:
            response = requests.get(
                f"{Config.API_BASE_URL}/users",
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            else:
                current_app.logger.error(f"Error fetching users from API: {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error connecting to API: {e}")
            return []
    
    def _create_user_in_api(self, user_data: Dict) -> Dict:
        """Crear usuario en la API (futuro)"""
        try:
            response = requests.post(
                f"{Config.API_BASE_URL}/users",
                json={
                    'username': user_data['username'],
                    'email': user_data['email'],  
                    'role_id': user_data['role_id']
                },
                timeout=10
            )
            if response.status_code == 201:
                return response.json()
            else:
                raise Exception(f"Error creating user: {response.status_code}")
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error creating user in API: {e}")
            raise