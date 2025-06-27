from enum import Enum
from typing import Dict, List, Set
import logging

logger = logging.getLogger(__name__)

class Module(Enum):
    """Módulos disponibles en la aplicación"""
    GEOGRAPHIC = "geographic"  # Países, ADM1, ADM2, Localizaciones
    CLIMATE_DATA = "climate_data"  # Datos climáticos 
    CROP_DATA = "crop_data"  # Datos de cultivos 
    USER_MANAGEMENT = "user_management"  # Usuarios y roles

class RolePermissionMapper:
    """Mapea roles de Keycloak con módulos accesibles en la aplicación"""
    
    # Definición simplificada: rol -> lista de módulos con acceso completo
    ROLE_MODULES: Dict[str, List[Module]] = {
        "adminsuper": [
            Module.GEOGRAPHIC,
            Module.USER_MANAGEMENT,
            Module.CROP_DATA,
            Module.CLIMATE_DATA,
        ],
        
        "admin": [
            Module.GEOGRAPHIC,
            Module.USER_MANAGEMENT,
            Module.CROP_DATA,
            Module.CLIMATE_DATA,
        ],
        
        "webadminsimple": [
            Module.GEOGRAPHIC,
        ],

        "Geo Admin": [
            Module.GEOGRAPHIC,
        ],
    }
    
    @classmethod
    def get_user_modules(cls, user_roles: List[str]) -> Set[Module]:
        """
        Obtiene los módulos accesibles combinados de todos los roles del usuario
        """
        accessible_modules = set()
        
        for role in user_roles:
            if role in cls.ROLE_MODULES:
                accessible_modules.update(cls.ROLE_MODULES[role])
        
        return accessible_modules
    
    @classmethod
    def user_has_module_access(cls, user_roles: List[str], module: Module) -> bool:
        """
        Verifica si el usuario tiene acceso al módulo
        """
        accessible_modules = cls.get_user_modules(user_roles)
        return module in accessible_modules
    
    @classmethod
    def get_available_roles(cls) -> List[str]:
        """
        Obtiene la lista de roles configurados
        """
        return list(cls.ROLE_MODULES.keys())
    
    @classmethod
    def get_role_modules(cls, role: str) -> List[Module]:
        """
        Obtiene los módulos a los que tiene acceso un rol específico
        """
        return cls.ROLE_MODULES.get(role, [])
    
    @classmethod
    def add_role(cls, role_name: str, modules: List[Module]) -> bool:
        """
        Agrega un nuevo rol con sus módulos
        """
        try:
            cls.ROLE_MODULES[role_name] = modules
            logger.info(f"Added role '{role_name}' with modules: {[m.value for m in modules]}")
            return True
        except Exception as e:
            logger.error(f"Error adding role '{role_name}': {e}")
            return False
    
    @classmethod
    def update_role(cls, role_name: str, modules: List[Module]) -> bool:
        """
        Actualiza los módulos de un rol existente
        """
        try:
            if role_name in cls.ROLE_MODULES:
                cls.ROLE_MODULES[role_name] = modules
                logger.info(f"Updated role '{role_name}' with modules: {[m.value for m in modules]}")
                return True
            else:
                logger.warning(f"Role '{role_name}' not found for update")
                return False
        except Exception as e:
            logger.error(f"Error updating role '{role_name}': {e}")
            return False
    
    @classmethod
    def remove_role(cls, role_name: str) -> bool:
        """
        Elimina un rol del mapeo
        """
        try:
            if role_name in cls.ROLE_MODULES:
                del cls.ROLE_MODULES[role_name]
                logger.info(f"Removed role '{role_name}' from mapping")
                return True
            else:
                logger.warning(f"Role '{role_name}' not found for removal")
                return False
        except Exception as e:
            logger.error(f"Error removing role '{role_name}': {e}")
            return False
    
    @classmethod
    def sync_with_keycloak_roles(cls, keycloak_roles: List[Dict]) -> Dict:
        """
        Sincroniza roles de Keycloak con el mapeo local y reporta diferencias
        """
        keycloak_role_names = {role.get('name') for role in keycloak_roles}
        configured_roles = set(cls.ROLE_MODULES.keys())
        
        missing_in_config = keycloak_role_names - configured_roles
        missing_in_keycloak = configured_roles - keycloak_role_names
        
        return {
            'synced_roles': keycloak_role_names & configured_roles,
            'missing_in_config': missing_in_config,
            'missing_in_keycloak': missing_in_keycloak,
            'total_keycloak_roles': len(keycloak_role_names),
            'total_configured_roles': len(configured_roles)
        }
    
    @classmethod
    def get_modules_info(cls) -> Dict:
        """
        Obtiene información de todos los módulos disponibles
        """
        return {
            module.value: {
                'name': module.name,
                'value': module.value,
                'description': cls._get_module_description(module)
            }
            for module in Module
        }
    
    @classmethod
    def _get_module_description(cls, module: Module) -> str:
        """
        Obtiene descripción amigable del módulo
        """
        descriptions = {
            Module.GEOGRAPHIC: "Gestión de países, estados, municipios y localizaciones",
            Module.CLIMATE_DATA: "Gestión de datos climáticos",
            Module.CROP_DATA: "Gestión de datos de cultivos",
            Module.USER_MANAGEMENT: "Administración de usuarios y roles",
        }
        return descriptions.get(module, module.value)