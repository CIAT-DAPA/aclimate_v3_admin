"""
Servicio para interactuar con la API de Keycloak vía endpoints externos
"""
import requests
from typing import Dict, List, Optional
from flask import current_app
import logging

logger = logging.getLogger(__name__)


class KeycloakAPIService:
    """Servicio para llamar a los endpoints de la API de Keycloak"""
    
    def __init__(self):
        self.api_base_url = None
    
    def _get_api_url(self) -> str:
        """Obtener la URL base de la API desde la configuración"""
        if not self.api_base_url:
            self.api_base_url = current_app.config.get('API_BASE_URL')
        return self.api_base_url
    
    def _get_headers(self, token: str) -> Dict:
        """Obtener headers para las peticiones"""
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    # ==================== USUARIOS ====================
    
    def create_user(
        self, 
        token: str,
        username: str,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        email_verified: bool = False,
        enabled: bool = True
    ) -> Optional[Dict]:
        """
        Crear un usuario en Keycloak vía API
        
        Args:
            token: Token de autenticación del usuario admin
            username: Nombre de usuario
            email: Email
            password: Contraseña
            first_name: Nombre
            last_name: Apellido
            email_verified: Si el email está verificado
            enabled: Si el usuario está habilitado
        
        Returns:
            Dict con user_id y mensaje, o None si hay error
        """
        try:
            url = f"{self._get_api_url()}/users/create-user"
            
            payload = {
                "username": username,
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
                "emailVerified": email_verified,
                "enabled": enabled,
                "credentials": [
                    {
                        "type": "password",
                        "value": password,
                        "temporary": False
                    }
                ]
            }
            
            logger.info(f"Creating user in Keycloak: {username}")
            
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(token),
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                logger.info(f"User created successfully: {result}")
                return result
            else:
                logger.error(f"Failed to create user: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating user in Keycloak: {e}")
            return None
    
    def update_user(
        self,
        token: str,
        user_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        email_verified: Optional[bool] = None,
        enabled: Optional[bool] = None
    ) -> bool:
        """
        Actualizar un usuario en Keycloak
        
        Args:
            token: Token de autenticación
            user_id: ID del usuario en Keycloak
            first_name: Nuevo nombre
            last_name: Nuevo apellido
            email: Nuevo email
            email_verified: Estado de verificación de email
            enabled: Estado habilitado/deshabilitado
        
        Returns:
            True si se actualizó correctamente
        """
        try:
            url = f"{self._get_api_url()}/users/edit-user/{user_id}"
            
            # Construir payload solo con campos proporcionados
            payload = {}
            if first_name is not None:
                payload['firstName'] = first_name
            if last_name is not None:
                payload['lastName'] = last_name
            if email is not None:
                payload['email'] = email
            if email_verified is not None:
                payload['emailVerified'] = email_verified
            if enabled is not None:
                payload['enabled'] = enabled
            
            if not payload:
                logger.warning("No fields provided for user update")
                return False
            
            logger.info(f"Updating user in Keycloak: {user_id}")
            
            response = requests.patch(
                url,
                json=payload,
                headers=self._get_headers(token),
                timeout=30
            )
            
            if response.status_code in [200, 204]:
                logger.info(f"User updated successfully: {user_id}")
                return True
            else:
                logger.error(f"Failed to update user: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating user in Keycloak: {e}")
            return False
    
    def delete_user(self, token: str, user_id: str) -> bool:
        """
        Eliminar un usuario de Keycloak
        
        Args:
            token: Token de autenticación
            user_id: ID del usuario en Keycloak
        
        Returns:
            True si se eliminó correctamente
        """
        try:
            url = f"{self._get_api_url()}/users/delete-user"
            
            payload = {
                "user_id": user_id
            }
            
            logger.info(f"Deleting user from Keycloak: {user_id}")
            
            response = requests.delete(
                url,
                json=payload,
                headers=self._get_headers(token),
                timeout=30
            )
            
            if response.status_code in [200, 204]:
                logger.info(f"User deleted successfully: {user_id}")
                return True
            else:
                logger.error(f"Failed to delete user: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting user from Keycloak: {e}")
            return False
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Obtener información de un usuario de Keycloak por su ID
        
        Args:
            user_id: ID del usuario en Keycloak
        
        Returns:
            Dict con la información del usuario o None si no se encuentra
        """
        try:
            # Necesitamos un token de admin para hacer esta consulta
            # Por ahora usaremos el token del usuario actual de la sesión
            from flask import session
            token = session.get('access_token')
            
            if not token:
                logger.warning("No access token available to get user from Keycloak")
                return None
            
            url = f"{self._get_api_url()}/users/get-user/{user_id}"
            
            logger.info(f"Getting user from Keycloak: {user_id}")
            
            response = requests.get(
                url,
                headers=self._get_headers(token),
                timeout=30
            )
            
            if response.status_code == 200:
                user = response.json()
                logger.info(f"User retrieved from Keycloak: {user_id}")
                return user
            else:
                logger.warning(f"Could not retrieve user {user_id}: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting user from Keycloak: {e}")
            return None
    
    def assign_role_to_user(self, token: str, user_id: str, role_id: str) -> bool:
        """
        Asignar un rol a un usuario en Keycloak
        
        Args:
            token: Token de autenticación
            user_id: ID del usuario en Keycloak
            role_id: ID del rol a asignar
        
        Returns:
            True si se asignó correctamente
        """
        try:
            url = f"{self._get_api_url()}/users/assign-role"
            
            payload = {
                "user_id": user_id,
                "role_id": role_id
            }
            
            logger.info(f"Assigning role {role_id} to user {user_id}")
            
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(token),
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Role assigned successfully to user {user_id}")
                return True
            else:
                logger.error(f"Failed to assign role: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error assigning role to user: {e}")
            return False
    
    # ==================== ROLES ====================
    
    def create_role(
        self,
        token: str,
        name: str,
        description: Optional[str] = None,
        composite: bool = False
    ) -> bool:
        """
        Crear un rol en Keycloak
        
        Args:
            token: Token de autenticación
            name: Nombre del rol
            description: Descripción del rol
            composite: Si es un rol compuesto
        
        Returns:
            True si se creó correctamente
        """
        try:
            url = f"{self._get_api_url()}/roles/create"
            
            payload = {
                "name": name,
                "description": description,
                "composite": composite
            }
            
            logger.info(f"Creating role in Keycloak: {name}")
            
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(token),
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Role created successfully: {name}")
                return True
            else:
                logger.error(f"Failed to create role: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating role in Keycloak: {e}")
            return False
    
    def delete_role(self, token: str, role_id: str) -> bool:
        """
        Eliminar un rol de Keycloak
        
        Args:
            token: Token de autenticación
            role_id: ID del rol
        
        Returns:
            True si se eliminó correctamente
        """
        try:
            url = f"{self._get_api_url()}/roles/delete/{role_id}"
            
            logger.info(f"Deleting role from Keycloak: {role_id}")
            
            response = requests.delete(
                url,
                headers=self._get_headers(token),
                timeout=30
            )
            
            if response.status_code in [200, 204]:
                logger.info(f"Role deleted successfully: {role_id}")
                return True
            else:
                logger.error(f"Failed to delete role: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting role from Keycloak: {e}")
            return False
