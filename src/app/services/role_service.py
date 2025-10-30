from typing import List, Dict, Optional
from flask import current_app, session
from aclimate_v3_orm.services.role_service import RoleService as ORMRoleService
from aclimate_v3_orm.schemas import RoleRead, RoleCreate, RoleUpdate
from aclimate_v3_orm.enums import Apps
from app.services.keycloak_api_service import KeycloakAPIService

class RoleService:
    """Servicio para manejar roles desde la base de datos ORM y Keycloak"""
    
    def __init__(self):
        self.orm_service = ORMRoleService()
        self.keycloak_api = KeycloakAPIService()
    
    def _role_to_dict(self, role: RoleRead) -> Dict:
        """Convierte RoleRead a diccionario para uso en la app"""
        return {
            'id': role.id,
            'name': role.name,
            'app': role.app.value if role.app else None,
            'display_name': role.name,
        }
    
    def get_all(self, app_filter: str = None) -> List[Dict]:
        """
        Obtener todos los roles
        
        Args:
            app_filter: Filtrar por aplicación (opcional)
        """
        try:
            if app_filter:
                roles = self.orm_service.get_by_app(app_filter)
            else:
                roles = self.orm_service.get_all()
            
            normalized_roles = [self._role_to_dict(role) for role in roles]
            
            current_app.logger.info(f"Successfully retrieved {len(normalized_roles)} roles")
            return normalized_roles
        except Exception as e:
            current_app.logger.error(f"Error getting roles: {e}")
            return []
    
    def get_by_id(self, role_id: int) -> Optional[Dict]:
        """Obtener rol por ID"""
        try:
            role = self.orm_service.get_by_id(role_id)
            if role:
                return self._role_to_dict(role)
            return None
        except Exception as e:
            current_app.logger.error(f"Error getting role {role_id}: {e}")
            return None
    
    def get_by_name(self, name: str, app: str = None) -> Optional[Dict]:
        """
        Obtener rol por nombre
        
        Args:
            name: Nombre del rol
            app: Aplicación del rol (opcional)
        """
        try:
            if app:
                role = self.orm_service.get_by_name_and_app(name, app)
            else:
                roles = self.orm_service.get_by_name(name)
                role = roles[0] if roles else None
            
            if role:
                return self._role_to_dict(role)
            return None
        except Exception as e:
            current_app.logger.error(f"Error getting role by name {name}: {e}")
            return None
    
    def create(self, name: str, app: str = 'aclimate_admin', **kwargs) -> Optional[Dict]:
        """
        Crear nuevo rol
        
        Args:
            name: Nombre del rol
            app: Aplicación (por defecto 'aclimate_admin')
            **kwargs: Parámetros adicionales ignorados (compatibilidad con código antiguo)
        
        Note:
            Los parámetros 'description' y 'modules' son ignorados.
            Los permisos ahora se manejan en la tabla user_access, no por rol.
        """
        try:
            # Validar que app sea un valor válido del enum
            try:
                app_enum = Apps(app)
            except ValueError:
                current_app.logger.error(f"Invalid app value: {app}")
                return None
            
            # Ignorar parámetros adicionales del sistema antiguo
            if 'description' in kwargs:
                current_app.logger.info(f"'description' parameter ignored (not supported in new system)")
            if 'modules' in kwargs:
                current_app.logger.info(f"'modules' parameter ignored (permissions now managed via user_access)")
            
            role_data = RoleCreate(name=name, app=app_enum)
            created_role = self.orm_service.create(role_data)
            
            current_app.logger.info(f"Role '{name}' created successfully")
            return self._role_to_dict(created_role)
        except Exception as e:
            current_app.logger.error(f"Error creating role: {e}")
            return None
    
    def update(self, role_id: int, name: str = None, app: str = None) -> Optional[Dict]:
        """
        Actualizar rol
        
        Args:
            role_id: ID del rol
            name: Nuevo nombre (opcional)
            app: Nueva aplicación (opcional)
        """
        try:
            update_data = {}
            if name:
                update_data['name'] = name
            if app:
                try:
                    update_data['app'] = Apps(app)
                except ValueError:
                    current_app.logger.error(f"Invalid app value: {app}")
                    return None
            
            if not update_data:
                current_app.logger.warning("No data provided for update")
                return None
            
            role_update = RoleUpdate(**update_data)
            updated_role = self.orm_service.update(role_id, role_update)
            
            if updated_role:
                current_app.logger.info(f"Role {role_id} updated successfully")
                return self._role_to_dict(updated_role)
            return None
        except Exception as e:
            current_app.logger.error(f"Error updating role {role_id}: {e}")
            return None
    
    def delete(self, role_id: int) -> bool:
        """Eliminar rol"""
        try:
            result = self.orm_service.delete(role_id)
            if result:
                current_app.logger.info(f"Role {role_id} deleted successfully")
            return result
        except Exception as e:
            current_app.logger.error(f"Error deleting role {role_id}: {e}")
            return False
    
    def get_roles_for_app(self, app: str = 'aclimate_admin') -> List[Dict]:
        """
        Obtener roles filtrados por aplicación
        
        Args:
            app: Nombre de la aplicación
        """
        return self.get_all(app_filter=app)
    
    # ==================== COMPATIBILIDAD CON CÓDIGO ANTIGUO ====================
    
    def get_role_with_modules(self, name: str) -> Optional[Dict]:
        """
        Compatibilidad: obtener información del rol junto con módulos.
        Nota: En la nueva arquitectura los permisos no se asignan al rol, sino
        por usuario/país/módulo (tabla user_access). Por lo tanto, aquí
        devolvemos el rol y una lista vacía de módulos para evitar rupturas.
        """
        role = self.get_by_name(name)
        if not role:
            return None
        # Asegurar campos esperados por la vista
        return {
            'id': role.get('id'),
            'name': role.get('name'),
            'app': role.get('app'),
            'display_name': role.get('display_name') or role.get('name'),
            'description': None,  # La descripción se gestiona en Keycloak
            'modules': [],        # Los módulos ya no se asignan a nivel de rol
        }
    
    def update_local_modules(self, name: str, modules: List[str]) -> bool:
        """
        Compatibilidad: método no-op para "actualizar" módulos de un rol.
        Mantiene compatibilidad con vistas antiguas; registra y devuelve True.
        """
        current_app.logger.info(
            "update_local_modules() llamado para '%s' con módulos %s. "
            "Este sistema ahora gestiona permisos por usuario (user_access).",
            name, modules
        )
        return True
    
    # ==================== MÉTODOS CON KEYCLOAK ====================
    
    def _get_current_user_token(self) -> Optional[str]:
        """Obtener el token del usuario actual de la sesión"""
        return session.get('access_token')
    
    def create_complete_role(
        self,
        name: str,
        description: Optional[str] = None,
        app: str = 'aclimate_admin',
        composite: bool = False
    ) -> Optional[Dict]:
        """
        Crear rol completo: primero en Keycloak, luego en BD local
        
        Args:
            name: Nombre del rol
            description: Descripción del rol
            app: Aplicación del rol
            composite: Si es un rol compuesto
        
        Returns:
            Dict con información del rol creado o None si falla
        """
        token = self._get_current_user_token()
        if not token:
            current_app.logger.error("No access token available for Keycloak API")
            return None
        
        try:
            # 1. Crear rol en Keycloak
            current_app.logger.info(f"Creating role in Keycloak: {name}")
            keycloak_success = self.keycloak_api.create_role(
                token=token,
                name=name,
                description=description,
                composite=composite
            )
            
            if not keycloak_success:
                current_app.logger.error("Failed to create role in Keycloak")
                return None
            
            current_app.logger.info(f"Role created in Keycloak: {name}")
            
            # 2. Crear rol en BD local
            current_app.logger.info(f"Creating role in local database")
            db_role = self.create(name=name, app=app)
            
            if not db_role:
                current_app.logger.error("Failed to create role in local database")
                # TODO: Considerar rollback - eliminar rol de Keycloak
                return None
            
            current_app.logger.info(f"Role created successfully: {name}")
            
            return db_role
            
        except Exception as e:
            current_app.logger.error(f"Error creating complete role: {e}")
            return None
    
    def delete_complete_role(self, role_id: int, keycloak_role_id: str) -> bool:
        """
        Eliminar rol de Keycloak y BD local
        
        Args:
            role_id: ID del rol en BD local
            keycloak_role_id: ID del rol en Keycloak
        
        Returns:
            True si se eliminó correctamente
        """
        token = self._get_current_user_token()
        if not token:
            current_app.logger.error("No access token available for Keycloak API")
            return False
        
        try:
            # 1. Eliminar de Keycloak
            current_app.logger.info(f"Deleting role from Keycloak: {keycloak_role_id}")
            keycloak_success = self.keycloak_api.delete_role(
                token=token,
                role_id=keycloak_role_id
            )
            
            if not keycloak_success:
                current_app.logger.warning("Failed to delete role from Keycloak, proceeding with local delete")
            
            # 2. Eliminar de BD local
            current_app.logger.info(f"Deleting role from local database: {role_id}")
            db_success = self.delete(role_id)
            
            if not db_success:
                current_app.logger.error("Failed to delete role from local database")
                return False
            
            current_app.logger.info(f"Role deleted successfully")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error deleting complete role: {e}")
            return False

