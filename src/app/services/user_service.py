from typing import List, Dict, Optional
from flask import current_app, session
from aclimate_v3_orm.services.user_service import UserService as ORMUserService
from aclimate_v3_orm.services.user_access_service import UserAccessService
from aclimate_v3_orm.services.role_service import RoleService as ORMRoleService
from aclimate_v3_orm.schemas import UserRead, UserCreate, UserUpdate, UserAccessRead
from app.services.keycloak_api_service import KeycloakAPIService

class UserService:
    """Servicio para manejar usuarios desde la base de datos ORM y Keycloak"""
    
    def __init__(self):
        self.orm_service = ORMUserService()
        self.access_service = UserAccessService()
        self.role_service = ORMRoleService()
        self.keycloak_api = KeycloakAPIService()
    
    def _user_to_dict(self, user: UserRead) -> Dict:
        """Convierte UserRead a diccionario para uso en la app"""
        user_dict = {
            'id': user.id,
            'keycloak_id': user.keycloak_ext_id,
            'role_id': user.role_id,
            'enabled': user.enable,
            'created_at': user.register if hasattr(user, 'register') else None,
            'updated_at': user.updated if hasattr(user, 'updated') else None,
        }
        
        # Add role information
        if user.role:
            user_dict['role_name'] = user.role.name
            user_dict['role_app'] = user.role.app.value if user.role.app else None
        
        # Add access information (countries and permissions)
        if user.accesses:
            user_dict['accesses'] = [
                {
                    'country_id': access.country_id,
                    'country_name': access.country.name if access.country else None,
                    'role_id': access.role_id,
                    'create': access.create,
                    'read': access.read,
                    'update': access.update,
                    'delete': access.delete,
                }
                for access in user.accesses
            ]
            
            # Extract unique countries
            countries = {}
            for access in user.accesses:
                if access.country_id not in countries:
                    countries[access.country_id] = {
                        'id': access.country_id,
                        'name': access.country.name if access.country else None
                    }
            user_dict['countries'] = list(countries.values())
        else:
            user_dict['accesses'] = []
            user_dict['countries'] = []
        
        return user_dict
    
    def get_all(self, enabled_only: bool = True) -> List[Dict]:
        """
        Obtener todos los usuarios con información de Keycloak
        
        Args:
            enabled_only: Si True, solo devuelve usuarios habilitados
        """
        try:
            users = self.orm_service.get_all_enable(enabled=enabled_only)
            normalized_users = []
            
            for user in users:
                user_dict = self._user_to_dict(user)
                
                # Enriquecer con datos de Keycloak
                try:
                    keycloak_user = self.keycloak_api.get_user_by_id(user.keycloak_ext_id)
                    if keycloak_user:
                        user_dict.update({
                            'username': keycloak_user.get('username'),
                            'email': keycloak_user.get('email'),
                            'first_name': keycloak_user.get('firstName'),
                            'last_name': keycloak_user.get('lastName'),
                            'enabled': keycloak_user.get('enabled', True)
                        })
                except Exception as e:
                    current_app.logger.warning(f"Could not fetch Keycloak data for user {user.id}: {e}")
                    # Si no se puede obtener de Keycloak, poner valores por defecto
                    user_dict.update({
                        'username': f'user_{user.id}',
                        'email': None,
                        'first_name': None,
                        'last_name': None,
                        'enabled': user.enable
                    })
                
                normalized_users.append(user_dict)
            
            current_app.logger.info(f"Successfully retrieved {len(normalized_users)} users")
            return normalized_users
        except Exception as e:
            current_app.logger.error(f"Error getting users: {e}")
            return []
    
    def get_by_id(self, user_id: int) -> Optional[Dict]:
        """Obtener usuario por ID de base de datos"""
        try:
            user = self.orm_service.get_by_id(user_id)
            if user:
                return self._user_to_dict(user)
            return None
        except Exception as e:
            current_app.logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    def get_by_keycloak_id(self, keycloak_id: str) -> Optional[Dict]:
        """Obtener usuario por ID de Keycloak"""
        try:
            users = self.orm_service.get_by_keycloak_ext_id(keycloak_id)
            if users:
                return self._user_to_dict(users[0])
            return None
        except Exception as e:
            current_app.logger.error(f"Error getting user by Keycloak ID {keycloak_id}: {e}")
            return None
    
    def get_by_role(self, role_id: int = None, role_name: str = None) -> List[Dict]:
        """
        Obtener usuarios por rol
        
        Args:
            role_id: ID del rol
            role_name: Nombre del rol
        """
        try:
            if role_id:
                users = self.orm_service.get_by_role_id(role_id)
            elif role_name:
                users = self.orm_service.get_by_role_name(role_name)
            else:
                current_app.logger.warning("No role criteria provided")
                return []
            
            normalized_users = [self._user_to_dict(user) for user in users]
            return normalized_users
        except Exception as e:
            current_app.logger.error(f"Error getting users by role: {e}")
            return []
    
    def create(self, keycloak_id: str, role_id: int, enabled: bool = True) -> Optional[Dict]:
        """
        Crear nuevo usuario en la base de datos
        
        Args:
            keycloak_id: ID del usuario en Keycloak
            role_id: ID del rol
            enabled: Si el usuario está habilitado
        """
        try:
            user_data = UserCreate(
                keycloak_ext_id=keycloak_id,
                role_id=role_id,
                enable=enabled
            )
            
            created_user = self.orm_service.create(user_data)
            
            current_app.logger.info(f"User created successfully with Keycloak ID: {keycloak_id}")
            return self._user_to_dict(created_user)
        except Exception as e:
            current_app.logger.error(f"Error creating user: {e}")
            return None
    
    def update(self, user_id: int, role_id: int = None, enabled: bool = None) -> Optional[Dict]:
        """
        Actualizar usuario
        
        Args:
            user_id: ID del usuario en la base de datos
            role_id: Nuevo rol (opcional)
            enabled: Nuevo estado (opcional)
        """
        try:
            update_data = {}
            if role_id is not None:
                update_data['role_id'] = role_id
            if enabled is not None:
                update_data['enable'] = enabled
            
            if not update_data:
                current_app.logger.warning("No data provided for update")
                return None
            
            user_update = UserUpdate(**update_data)
            updated_user = self.orm_service.update(user_id, user_update)
            
            if updated_user:
                current_app.logger.info(f"User {user_id} updated successfully")
                return self._user_to_dict(updated_user)
            return None
        except Exception as e:
            current_app.logger.error(f"Error updating user {user_id}: {e}")
            return None
    
    def delete(self, user_id: int) -> bool:
        """Deshabilitar usuario (soft delete)"""
        try:
            result = self.orm_service.delete(user_id)
            if result:
                current_app.logger.info(f"User {user_id} disabled successfully")
            return result
        except Exception as e:
            current_app.logger.error(f"Error deleting user {user_id}: {e}")
            return False
    
    def get_user_countries(self, user_id: int) -> List[Dict]:
        """Obtener países a los que el usuario tiene acceso"""
        try:
            accesses = self.access_service.get_by_user_id(user_id)
            
            countries = {}
            for access in accesses:
                country_id = access.country_id
                if country_id not in countries:
                    countries[country_id] = {
                        'id': country_id,
                        'name': access.country.name if access.country else None
                    }
            
            return list(countries.values())
        except Exception as e:
            current_app.logger.error(f"Error getting user countries: {e}")
            return []
    
    # ==================== MÉTODOS CON KEYCLOAK ====================
    
    def _get_current_user_token(self) -> Optional[str]:
        """Obtener el token del usuario actual de la sesión"""
        return session.get('access_token')
    
    def create_complete_user(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role_id: int,
        enabled: bool = True
    ) -> Optional[Dict]:
        """
        Crear usuario completo: primero en Keycloak, luego en BD local
        
        Args:
            username: Nombre de usuario
            email: Email del usuario
            password: Contraseña
            first_name: Nombre
            last_name: Apellido
            role_id: ID del rol en la BD local
            enabled: Si el usuario está habilitado
        
        Returns:
            Dict con información del usuario creado o None si falla
        """
        token = self._get_current_user_token()
        if not token:
            current_app.logger.error("No access token available for Keycloak API")
            return None
        
        try:
            # 1. Crear usuario en Keycloak
            current_app.logger.info(f"Creating user in Keycloak: {username}")
            keycloak_result = self.keycloak_api.create_user(
                token=token,
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                enabled=enabled
            )
            
            if not keycloak_result or 'user_id' not in keycloak_result:
                current_app.logger.error("Failed to create user in Keycloak")
                return None
            
            keycloak_user_id = keycloak_result['user_id']
            current_app.logger.info(f"User created in Keycloak with ID: {keycloak_user_id}")
            
            # 2. Crear usuario en BD local
            current_app.logger.info(f"Creating user in local database")
            db_user = self.create(
                keycloak_id=keycloak_user_id,
                role_id=role_id,
                enabled=enabled
            )
            
            if not db_user:
                current_app.logger.error("Failed to create user in local database")
                # TODO: Considerar rollback - eliminar usuario de Keycloak
                return None
            
            current_app.logger.info(f"User created successfully: {username}")
            
            return {
                'keycloak_id': keycloak_user_id,
                'db_id': db_user['id'],
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'role_id': role_id,
                'enabled': enabled
            }
            
        except Exception as e:
            current_app.logger.error(f"Error creating complete user: {e}")
            return None
    
    def update_complete_user(
        self,
        db_user_id: int,
        keycloak_user_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        role_id: Optional[int] = None,
        enabled: Optional[bool] = None
    ) -> bool:
        """
        Actualizar usuario en Keycloak y BD local
        
        Args:
            db_user_id: ID del usuario en BD local
            keycloak_user_id: ID del usuario en Keycloak
            first_name: Nuevo nombre
            last_name: Nuevo apellido
            email: Nuevo email
            role_id: Nuevo rol
            enabled: Nuevo estado
        
        Returns:
            True si se actualizó correctamente
        """
        token = self._get_current_user_token()
        if not token:
            current_app.logger.error("No access token available for Keycloak API")
            return False
        
        try:
            # 1. Actualizar en Keycloak
            if first_name or last_name or email or enabled is not None:
                current_app.logger.info(f"Updating user in Keycloak: {keycloak_user_id}")
                keycloak_success = self.keycloak_api.update_user(
                    token=token,
                    user_id=keycloak_user_id,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    enabled=enabled
                )
                
                if not keycloak_success:
                    current_app.logger.error("Failed to update user in Keycloak")
                    return False
            
            # 2. Actualizar en BD local
            if role_id is not None or enabled is not None:
                current_app.logger.info(f"Updating user in local database: {db_user_id}")
                db_user = self.update(
                    user_id=db_user_id,
                    role_id=role_id,
                    enabled=enabled
                )
                
                if not db_user:
                    current_app.logger.error("Failed to update user in local database")
                    return False
            
            current_app.logger.info(f"User updated successfully")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error updating complete user: {e}")
            return False
    
    def delete_complete_user(self, db_user_id: int, keycloak_user_id: str) -> bool:
        """
        Eliminar usuario de Keycloak y deshabilitar en BD local
        
        Args:
            db_user_id: ID del usuario en BD local
            keycloak_user_id: ID del usuario en Keycloak
        
        Returns:
            True si se eliminó correctamente
        """
        token = self._get_current_user_token()
        if not token:
            current_app.logger.error("No access token available for Keycloak API")
            return False
        
        try:
            # 1. Eliminar de Keycloak
            current_app.logger.info(f"Deleting user from Keycloak: {keycloak_user_id}")
            keycloak_success = self.keycloak_api.delete_user(
                token=token,
                user_id=keycloak_user_id
            )
            
            if not keycloak_success:
                current_app.logger.warning("Failed to delete user from Keycloak, proceeding with local delete")
            
            # 2. Deshabilitar en BD local (soft delete)
            current_app.logger.info(f"Disabling user in local database: {db_user_id}")
            db_success = self.delete(db_user_id)
            
            if not db_success:
                current_app.logger.error("Failed to disable user in local database")
                return False
            
            current_app.logger.info(f"User deleted/disabled successfully")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error deleting complete user: {e}")
            return False
    
    def assign_role_to_keycloak_user(
        self,
        keycloak_user_id: str,
        keycloak_role_id: str
    ) -> bool:
        """
        Asignar un rol de Keycloak a un usuario
        
        Args:
            keycloak_user_id: ID del usuario en Keycloak
            keycloak_role_id: ID del rol en Keycloak
        
        Returns:
            True si se asignó correctamente
        """
        token = self._get_current_user_token()
        if not token:
            current_app.logger.error("No access token available for Keycloak API")
            return False
        
        try:
            current_app.logger.info(f"Assigning role to user in Keycloak")
            success = self.keycloak_api.assign_role_to_user(
                token=token,
                user_id=keycloak_user_id,
                role_id=keycloak_role_id
            )
            
            if success:
                current_app.logger.info(f"Role assigned successfully")
            else:
                current_app.logger.error("Failed to assign role")
            
            return success
            
        except Exception as e:
            current_app.logger.error(f"Error assigning role to user: {e}")
            return False
