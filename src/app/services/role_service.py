from typing import List, Dict, Optional
from datetime import datetime
import requests
from flask import current_app, session
from config import Config

class RoleService:
    """Servicio para manejar roles - preparado para API"""
    
    def __init__(self):
        # Datos simulados como fallback
        self._fallback_roles = [
            {
                'id': 1,
                'name': 'Admin',
                'description': 'Administrador del sistema con acceso completo',
                'modules': {
                    'geographic': True,
                    'crops': True,
                    'weather': True,
                    'users': True,
                    'api': True,   
                },
                'enable': True,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            {
                'id': 2,
                'name': 'Geo Admin',
                'description': 'Usuario con acceso limitado a módulos geográficos',
                'modules': {
                    'geographic': True,
                    'crops': False,
                    'weather': False,
                    'users': False,
                    'api': False,   
                },
                'enable': True,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            {
                'id': 3,
                'name': 'Guest',
                'description': 'Invitado con acceso muy limitado',
                'modules': {
                    'geographic': False,
                    'crops': False,
                    'weather': False,
                    'users': False,
                    'api': False,   
                },
                'enable': True,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
        ]
        self._next_id = 4
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Obtener headers de autenticación"""
        token = session.get('access_token')
        if token:
            return {'Authorization': f'Bearer {token}'}
        return {}
    
    def get_all(self) -> List[Dict]:
        """Obtener todos los roles"""
        # TODO: Cuando la API esté lista, usar:
        try:
            response = requests.get(
                f"{Config.API_BASE_URL}/roles/get-roles",
                headers=self._get_auth_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('roles', [])
            else:
                # Fallback a datos simulados
                return self._fallback_roles.copy()
                
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error connecting to roles API: {e}")
            return self._fallback_roles.copy()
    
    def get_active_roles(self) -> List[Dict]:
        """Obtener solo los roles activos"""
        all_roles = self.get_all()
        return [role for role in all_roles if role.get('enable', True)]
    
    def get_by_id(self, role_id: int) -> Optional[Dict]:
        """Obtener rol por ID"""
        all_roles = self.get_all()
        for role in all_roles:
            if role['id'] == role_id:
                return role
        return None
    
    def get_by_name(self, name: str) -> Optional[Dict]:
        """Obtener rol por nombre"""
        all_roles = self.get_all()
        for role in all_roles:
            if role['name'].lower() == name.lower():
                return role
        return None
    
    def create(self, role_data: Dict) -> Dict:
        """Crear nuevo rol"""
        # TODO: Cuando la API esté lista, usar:
        try:
            response = requests.post(
                f"{Config.API_BASE_URL}/roles/create-role",
                headers=self._get_auth_headers(),
                json=role_data,
                timeout=10
            )
            
            if response.status_code == 201:
                return response.json()
            elif response.status_code == 400:
                error_data = response.json()
                raise ValueError(error_data.get('message', 'Error creating role'))
            else:
                raise Exception(f"Error creating role: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error creating role in API: {e}")
            # Fallback: crear en memoria
            return self._create_fallback(role_data)
        except ValueError:
            raise  # Re-raise validation errors
    
    def update(self, role_id: int, role_data: Dict) -> Optional[Dict]:
        """Actualizar rol existente"""
        # TODO: Cuando la API esté lista, usar:
        try:
            response = requests.put(
                f"{Config.API_BASE_URL}/roles/update-role/{role_id}",
                headers=self._get_auth_headers(),
                json=role_data,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                error_data = response.json()
                raise ValueError(error_data.get('message', 'Error updating role'))
            else:
                return None
                
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error updating role in API: {e}")
            return self._update_fallback(role_id, role_data)
        except ValueError:
            raise  # Re-raise validation errors
    
    def delete(self, role_id: int) -> bool:
        """Eliminar rol"""
        # TODO: Cuando la API esté lista, usar:
        try:
            response = requests.delete(
                f"{Config.API_BASE_URL}/roles/delete-role/{role_id}",
                headers=self._get_auth_headers(),
                timeout=10
            )
            
            return response.status_code == 200
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error deleting role in API: {e}")
            return self._delete_fallback(role_id)
    
    def restore(self, role_id: int) -> bool:
        """Restaurar rol deshabilitado"""
        # TODO: Cuando la API esté lista, usar endpoint específico
        return self.update(role_id, {'enable': True}) is not None
    
    # Métodos fallback para cuando la API no esté disponible
    def _create_fallback(self, role_data: Dict) -> Dict:
        """Crear rol en fallback (memoria)"""
        if any(r['name'].lower() == role_data['name'].lower() for r in self._fallback_roles):
            raise ValueError(f"Ya existe un rol con el nombre '{role_data['name']}'")
        
        default_modules = {
            'geographic': False,
            'crops': False,
            'weather': False,
            'users': False,
            'api': False,
        }
        
        new_role = {
            'id': self._next_id,
            'name': role_data['name'],
            'description': role_data.get('description', ''),
            'modules': role_data.get('modules', default_modules),
            'enable': role_data.get('enable', True),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        self._fallback_roles.append(new_role)
        self._next_id += 1
        
        return new_role.copy()
    
    def _update_fallback(self, role_id: int, role_data: Dict) -> Optional[Dict]:
        """Actualizar rol en fallback"""
        for i, role in enumerate(self._fallback_roles):
            if role['id'] == role_id:
                if 'name' in role_data and role_data['name'] != role['name']:
                    existing = self.get_by_name(role_data['name'])
                    if existing and existing['id'] != role_id:
                        raise ValueError(f"Ya existe un rol con el nombre '{role_data['name']}'")
                
                # Actualizar campos
                for field in ['name', 'description', 'modules', 'enable']:
                    if field in role_data:
                        self._fallback_roles[i][field] = role_data[field]
                
                self._fallback_roles[i]['updated_at'] = datetime.now()
                return self._fallback_roles[i].copy()
        
        return None
    
    def _delete_fallback(self, role_id: int) -> bool:
        """Eliminar rol en fallback"""
        for i, role in enumerate(self._fallback_roles):
            if role['id'] == role_id:
                self._fallback_roles[i]['enable'] = False
                self._fallback_roles[i]['updated_at'] = datetime.now()
                return True
        return False
    
    # Métodos utilitarios que permanecen igual
    def get_available_modules(self) -> List[str]:
        """Obtener lista de módulos disponibles"""
        return ['geographic', 'crops', 'weather', 'users', 'api']
    
    def has_module_access(self, role_id: int, module_name: str) -> bool:
        """Verificar si un rol tiene acceso a un módulo específico"""
        role = self.get_by_id(role_id)
        if role and role.get('enable', True):
            return role.get('modules', {}).get(module_name, False)
        return False
    
    def get_role_modules(self, role_id: int) -> Dict[str, bool]:
        """Obtener todos los módulos de un rol"""
        role = self.get_by_id(role_id)
        if role:
            return role.get('modules', {})
        return {}
    
    def get_roles_with_module_access(self, module_name: str) -> List[Dict]:
        """Obtener todos los roles que tienen acceso a un módulo específico"""
        all_roles = self.get_all()
        roles_with_access = []
        for role in all_roles:
            if role.get('enable', True) and role.get('modules', {}).get(module_name, False):
                roles_with_access.append(role)
        return roles_with_access