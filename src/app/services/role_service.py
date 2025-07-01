from typing import List, Dict
import requests
from flask import current_app, session
from config import Config
from app.config.permissions import RolePermissionMapper, Module

class RoleService:
    """Servicio para manejar roles desde la API y sincronización local"""
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Obtener headers de autenticación"""
        token = session.get('access_token')
        if token:
            return {'Authorization': f'Bearer {token}'}
        return {}
    
    def _normalize_role_data(self, api_role: Dict) -> Dict:
        """Convierte la estructura de la API a la estructura interna"""
        role_name = api_role.get('name', '')
        return {
            'id': api_role.get('id'),
            'name': role_name,
            'display_name': role_name,  # Usar el mismo nombre que viene de la API
            'description': api_role.get('description', ''),
            'composite': api_role.get('composite', False),
            'client_role': api_role.get('clientRole', True),
            'container_id': api_role.get('containerId', ''),
            'modules': RolePermissionMapper.get_role_modules(role_name),  # Agregar módulos locales
            'has_local_config': role_name in RolePermissionMapper.get_available_roles()
        }
    
    def get_all(self) -> List[Dict]:
        """Obtener todos los roles desde la API con información local"""
        try:
            response = requests.get(
                f"{Config.API_BASE_URL}/users/get-client-roles",
                headers=self._get_auth_headers(),
                timeout=10
            )
            
            current_app.logger.info(f"Roles API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                api_response = response.json()
                
                # Manejar diferentes formatos de respuesta
                roles_data = []
                
                if isinstance(api_response, list):
                    # Respuesta directa como lista
                    roles_data = api_response
                elif isinstance(api_response, dict):
                    # Respuesta como diccionario, buscar la lista de roles
                    roles_data = (api_response.get('roles') or 
                                api_response.get('data') or 
                                api_response.get('items') or 
                                [api_response])
                
                # Normalizar datos y agregar información local
                normalized_roles = []
                for role in roles_data:
                    if isinstance(role, dict):
                        normalized_role = self._normalize_role_data(role)
                        normalized_roles.append(normalized_role)
                
                current_app.logger.info(f"Successfully retrieved {len(normalized_roles)} roles")
                return normalized_roles
            else:
                current_app.logger.error(f"Error from roles API: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Network error getting roles: {e}")
            return []
        except Exception as e:
            current_app.logger.error(f"Unexpected error getting roles: {e}")
            return []

    def create(self, name: str, description: str = None, modules: List[str] = None) -> Dict:
        """Crear rol en Keycloak y en configuración local"""
        try:
            # 1. Crear rol en Keycloak
            role_data = {
                'name': name,
                'description': description or '',
                'composite': False
            }
            
            response = requests.post(
                f"{Config.API_BASE_URL}/roles/create",
                headers=self._get_auth_headers(),
                json=role_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                current_app.logger.info(f"Role '{name}' created successfully in Keycloak")
                
                # 2. Agregar rol a configuración local si se especificaron módulos
                if modules:
                    # Convertir strings de módulos a objetos Module
                    module_objects = []
                    for module_str in modules:
                        try:
                            module_obj = Module(module_str)
                            module_objects.append(module_obj)
                        except ValueError:
                            current_app.logger.warning(f"Invalid module: {module_str}")
                    
                    # Agregar a configuración local
                    if module_objects:
                        success = RolePermissionMapper.add_role(name, module_objects)
                        if success:
                            current_app.logger.info(f"Role '{name}' added to local configuration with modules: {[m.value for m in module_objects]}")
                        else:
                            current_app.logger.warning(f"Failed to add role '{name}' to local configuration")
                
                return {
                    'success': True,
                    'role': self._normalize_role_data({
                        'name': name,
                        'description': description,
                        'id': response.json().get('id') if response.content else None
                    })
                }
            else:
                current_app.logger.error(f"Error creating role in Keycloak: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"Error from API: {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Network error creating role: {e}")
            return {
                'success': False,
                'error': f"Network error: {str(e)}"
            }
        except Exception as e:
            current_app.logger.error(f"Unexpected error creating role: {e}")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }
        
    def update_local_modules(self, role_name: str, modules: List[str]) -> bool:
        """Actualizar módulos de un rol en la configuración local"""
        try:
            # Convertir strings de módulos a objetos Module
            module_objects = []
            for module_str in modules:
                try:
                    module_obj = Module(module_str)
                    module_objects.append(module_obj)
                except ValueError:
                    current_app.logger.warning(f"Invalid module: {module_str}")
            
            # Actualizar configuración local
            success = RolePermissionMapper.update_role(role_name, module_objects)
            if success:
                current_app.logger.info(f"Updated local modules for role '{role_name}': {[m.value for m in module_objects]}")
            
            return success
            
        except Exception as e:
            current_app.logger.error(f"Error updating local modules for role '{role_name}': {e}")
            return False

    def delete(self, role_id: str, role_name: str = None) -> bool:
        """Eliminar rol de Keycloak y configuración local"""
        try:
            # 1. Eliminar de Keycloak
            response = requests.delete(
                f"{Config.API_BASE_URL}/users/delete-client-role/{role_id}",
                headers=self._get_auth_headers(),
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                current_app.logger.info(f"Role '{role_name or role_id}' deleted successfully from Keycloak")
                
                # 2. Eliminar de configuración local si tenemos el nombre
                if role_name:
                    success = RolePermissionMapper.remove_role(role_name)
                    if success:
                        current_app.logger.info(f"Role '{role_name}' removed from local configuration")
                    else:
                        current_app.logger.warning(f"Role '{role_name}' not found in local configuration")
                
                return True
            else:
                current_app.logger.error(f"Error deleting role from Keycloak: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Network error deleting role: {e}")
            return False
        except Exception as e:
            current_app.logger.error(f"Unexpected error deleting role: {e}")
            return False
        
    def get_role_with_modules(self, role_name: str) -> Dict:
        """Obtener información completa de un rol incluyendo módulos"""
        roles = self.get_all()
        for role in roles:
            if role['name'] == role_name:
                return role
        return None
    
    def sync_role_modules(self) -> Dict:
        """Sincronizar roles entre Keycloak y configuración local"""
        try:
            keycloak_roles = self.get_all()
            sync_result = RolePermissionMapper.sync_with_keycloak_roles(keycloak_roles)
            
            current_app.logger.info(f"Role synchronization completed: {sync_result}")
            return {
                'success': True,
                'sync_result': sync_result
            }
            
        except Exception as e:
            current_app.logger.error(f"Error during role synchronization: {e}")
            return {
                'success': False,
                'error': str(e)
            }