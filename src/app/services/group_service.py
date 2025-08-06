from typing import List, Dict
import requests
from flask import current_app, session
from config import Config

class GroupService:
    """Servicio para manejar grupos/países desde la API de Keycloak"""
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Obtener headers de autenticación"""
        token = session.get('access_token')
        if token:
            return {'Authorization': f'Bearer {token}'}
        return {}
    
    def _normalize_group_data(self, api_group: Dict) -> Dict:
        """Convierte la estructura de la API a la estructura interna"""
        group_name = api_group.get('name', '')
        
        # Extraer nombre del país del nombre del grupo
        # Ejemplo: "aclimate_admin_colombia" -> "Colombia"
        country_name = self._extract_country_name(group_name)
        
        return {
            'id': api_group.get('id'),
            'name': group_name,
            'display_name': country_name,
            'country_name': country_name
        }
    
    def _extract_country_name(self, group_name: str) -> str:
        """Extrae el nombre del país del nombre del grupo"""
        # Remover prefijos comunes y capitalizar
        if 'aclimate_admin_' in group_name.lower():
            country = group_name.lower().replace('aclimate_admin_', '')
            return country.capitalize()
        
        # Si no tiene el prefijo esperado, usar el nombre completo capitalizado
        return group_name.replace('_', ' ').title()
    
    def get_all(self) -> List[Dict]:
        """Obtener todos los grupos/países desde la API"""
        try:
            response = requests.get(
                f"{Config.API_BASE_URL}/groups/list",
                headers=self._get_auth_headers(),
                timeout=10
            )
            
            current_app.logger.info(f"Groups API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                api_response = response.json()
                
                # Manejar diferentes formatos de respuesta
                groups_data = []
                
                if isinstance(api_response, list):
                    # Respuesta directa como lista
                    groups_data = api_response
                elif isinstance(api_response, dict):
                    # Respuesta como diccionario, buscar la lista de grupos
                    groups_data = (api_response.get('groups') or 
                                 api_response.get('data') or 
                                 api_response.get('items') or 
                                 [api_response])
                
                # Normalizar datos
                normalized_groups = []
                for group in groups_data:
                    if isinstance(group, dict):
                        normalized_group = self._normalize_group_data(group)
                        normalized_groups.append(normalized_group)
                
                current_app.logger.info(f"Successfully retrieved {len(normalized_groups)} groups")
                return normalized_groups
            else:
                current_app.logger.error(f"Error from groups API: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Network error getting groups: {e}")
            return []
        except Exception as e:
            current_app.logger.error(f"Unexpected error getting groups: {e}")
            return []
    
    def create_group(self, group_name: str) -> bool:
        """Crear un nuevo grupo/país"""
        try:
            data = {
                "group_name": group_name
            }
            
            current_app.logger.info(f"Creating group: {group_name}")
            
            headers = self._get_auth_headers()
            headers['Content-Type'] = 'application/json'
            
            response = requests.post(
                f"{Config.API_BASE_URL}/groups/create",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                current_app.logger.info(f"Successfully created group: {group_name}")
                return True
            else:
                current_app.logger.error(f"Error creating group: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Network error creating group: {e}")
            return False
        except Exception as e:
            current_app.logger.error(f"Unexpected error creating group: {e}")
            return False
    
    def assign_user_to_groups(self, user_id: str, group_names: List[str]) -> bool:
        """Asignar usuario a grupos específicos"""
        try:
            data = {
                "user_id": user_id,
                "groups": group_names
            }
            
            current_app.logger.info(f"Assigning user {user_id} to groups: {group_names}")
            
            headers = self._get_auth_headers()
            headers['Content-Type'] = 'application/json'
            
            response = requests.post(
                f"{Config.API_BASE_URL}/users/assign-groups",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code in [200, 201, 204]:
                current_app.logger.info(f"Successfully assigned user {user_id} to groups")
                return True
            else:
                current_app.logger.error(f"Error assigning user to groups: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Network error assigning user to groups: {e}")
            return False
        except Exception as e:
            current_app.logger.error(f"Unexpected error assigning user to groups: {e}")
            return False
    
    def remove_user_from_groups(self, user_id: str, group_names: List[str]) -> bool:
        """Remover usuario de grupos específicos"""
        try:
            data = {
                "user_id": user_id,
                "groups": group_names
            }
            
            current_app.logger.info(f"Removing user {user_id} from groups: {group_names}")
            
            headers = self._get_auth_headers()
            headers['Content-Type'] = 'application/json'
            
            response = requests.delete(
                f"{Config.API_BASE_URL}/users/remove-groups",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                current_app.logger.info(f"Successfully removed user {user_id} from groups")
                return True
            else:
                current_app.logger.error(f"Error removing user from groups: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Network error removing user from groups: {e}")
            return False
        except Exception as e:
            current_app.logger.error(f"Unexpected error removing user from groups: {e}")
            return False
    
    def update_user_groups(self, user_id: str, new_group_names: List[str]) -> bool:
        """Actualizar completamente los grupos de un usuario
        
        Nota: Esta función utiliza el servicio de usuarios para obtener 
        los grupos actuales del usuario
        """
        try:
            from app.services.user_service import UserService
            
            # Obtener información actual del usuario incluyendo sus grupos
            user_service = UserService()
            user_data = user_service.get_user_by_id(user_id)
            
            if not user_data:
                current_app.logger.error(f"Could not get user data for {user_id}")
                return False
            
            # Obtener nombres de grupos actuales
            current_groups = user_data.get('groups', [])
            current_group_names = [group.get('name', '') for group in current_groups]
            
            # Calcular grupos a agregar y remover
            groups_to_add = [name for name in new_group_names if name not in current_group_names]
            groups_to_remove = [name for name in current_group_names if name not in new_group_names]
            
            success = True
            
            # Remover grupos que ya no debe tener
            if groups_to_remove:
                if not self.remove_user_from_groups(user_id, groups_to_remove):
                    success = False
            
            # Agregar nuevos grupos
            if groups_to_add:
                if not self.assign_user_to_groups(user_id, groups_to_add):
                    success = False
            
            return success
            
        except Exception as e:
            current_app.logger.error(f"Error updating user groups: {e}")
            return False
    
    def get_group_by_name(self, group_name: str) -> Dict:
        """Obtener información de un grupo específico por nombre"""
        try:
            all_groups = self.get_all()
            for group in all_groups:
                if group['name'] == group_name:
                    return group
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error getting group by name: {e}")
            return None
    
    def get_groups_by_names(self, group_names: List[str]) -> List[Dict]:
        """Obtener grupos por nombres"""
        try:
            all_groups = self.get_all()
            found_groups = []
            
            for group in all_groups:
                if group['name'] in group_names:
                    found_groups.append(group)
            
            return found_groups
            
        except Exception as e:
            current_app.logger.error(f"Error getting groups by names: {e}")
            return []