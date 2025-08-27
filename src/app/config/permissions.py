from enum import Enum
from typing import Dict, List, Set
import logging
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class Module(Enum):
    """Módulos disponibles en la aplicación"""
    GEOGRAPHIC = "geographic"  # Países, ADM1, ADM2, Localizaciones
    CLIMATE_DATA = "climate_data"  # Datos climáticos 
    CROP_DATA = "crop_data"  # Datos de cultivos 
    STRESS_DATA = "stress_data"  # Datos de estreses
    PHENOLOGICAL_STAGE = "phenological_stage"  # Etapas fenológicas 
    USER_MANAGEMENT = "user_management"  # Usuarios y roles
    CONFIGURATION = "configuration"  # Configuración del sistema

class RolePermissionMapper:
    """Mapea roles de Keycloak con módulos accesibles en la aplicación"""
    
    # Archivo donde se almacena la configuración persistente
    _CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'role_modules_config.json')
    
    # Configuración por defecto (roles del sistema)
    _DEFAULT_ROLE_MODULES: Dict[str, List[str]] = {
        "adminsuper": [
            Module.GEOGRAPHIC.value,
            Module.USER_MANAGEMENT.value,
            Module.CROP_DATA.value,
            Module.STRESS_DATA.value,
            Module.PHENOLOGICAL_STAGE.value,
            Module.CLIMATE_DATA.value,
            Module.CONFIGURATION.value,
        ],
        
        "admin": [
            Module.GEOGRAPHIC.value,
            Module.USER_MANAGEMENT.value,
            Module.CROP_DATA.value,
            Module.STRESS_DATA.value,
            Module.PHENOLOGICAL_STAGE.value,
            Module.CLIMATE_DATA.value,
            Module.CONFIGURATION.value,
        ],
        
        "webadminsimple": [
            Module.GEOGRAPHIC.value,
        ],

        "Geo Admin": [
            Module.GEOGRAPHIC.value,
        ],
    }
    
    @classmethod
    def _load_config(cls) -> Dict[str, List[str]]:
        """Carga la configuración desde el archivo JSON"""
        try:
            config_path = Path(cls._CONFIG_FILE)
            
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    stored_config = json.load(f)
                    
                # Combinar configuración por defecto con la almacenada
                combined_config = cls._DEFAULT_ROLE_MODULES.copy()
                combined_config.update(stored_config)
                
                logger.info(f"Loaded role configuration from {config_path} with {len(combined_config)} roles")
                return combined_config
            else:
                # Si no existe el archivo, usar configuración por defecto y crearla
                cls._save_config(cls._DEFAULT_ROLE_MODULES)
                logger.info(f"Created new configuration file at {config_path}")
                return cls._DEFAULT_ROLE_MODULES.copy()
                
        except Exception as e:
            logger.error(f"Error loading configuration from {cls._CONFIG_FILE}: {e}")
            logger.info("Using default configuration")
            return cls._DEFAULT_ROLE_MODULES.copy()
    
    @classmethod
    def _save_config(cls, config: Dict[str, List[str]]) -> bool:
        """Guarda la configuración en el archivo JSON"""
        try:
            config_path = Path(cls._CONFIG_FILE)
            
            # Crear directorio si no existe
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Filtrar roles del sistema para no almacenarlos en el archivo
            # (estos siempre se cargan desde _DEFAULT_ROLE_MODULES)
            filtered_config = {
                role: modules for role, modules in config.items()
                if role not in cls._DEFAULT_ROLE_MODULES
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(filtered_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved role configuration to {config_path} with {len(filtered_config)} custom roles")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration to {cls._CONFIG_FILE}: {e}")
            return False
    
    @classmethod
    def _get_current_config(cls) -> Dict[str, List[str]]:
        """Obtiene la configuración actual (cargada desde archivo)"""
        return cls._load_config()
    
    @classmethod
    def _modules_from_strings(cls, module_strings: List[str]) -> List[Module]:
        """Convierte lista de strings a lista de objetos Module"""
        modules = []
        for module_str in module_strings:
            try:
                modules.append(Module(module_str))
            except ValueError:
                logger.warning(f"Invalid module string: {module_str}")
        return modules
    
    @classmethod
    def _modules_to_strings(cls, modules: List[Module]) -> List[str]:
        """Convierte lista de objetos Module a lista de strings"""
        return [module.value for module in modules]
    
    @classmethod
    def get_user_modules(cls, user_roles: List[str]) -> Set[Module]:
        """
        Obtiene los módulos accesibles combinados de todos los roles del usuario
        """
        accessible_modules = set()
        config = cls._get_current_config()
        
        for role in user_roles:
            if role in config:
                role_modules = cls._modules_from_strings(config[role])
                accessible_modules.update(role_modules)
        
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
        config = cls._get_current_config()
        return list(config.keys())
    
    @classmethod
    def get_role_modules(cls, role: str) -> List[Module]:
        """
        Obtiene los módulos a los que tiene acceso un rol específico
        """
        config = cls._get_current_config()
        module_strings = config.get(role, [])
        return cls._modules_from_strings(module_strings)
    
    @classmethod
    def add_role(cls, role_name: str, modules: List[Module]) -> bool:
        """
        Agrega un nuevo rol con sus módulos (persistente)
        """
        try:
            config = cls._get_current_config()
            config[role_name] = cls._modules_to_strings(modules)
            
            if cls._save_config(config):
                logger.info(f"Added role '{role_name}' with modules: {[m.value for m in modules]}")
                return True
            else:
                logger.error(f"Failed to save configuration after adding role '{role_name}'")
                return False
                
        except Exception as e:
            logger.error(f"Error adding role '{role_name}': {e}")
            return False
    
    @classmethod
    def update_role(cls, role_name: str, modules: List[Module]) -> bool:
        """
        Actualiza los módulos de un rol existente (persistente)
        """
        try:
            config = cls._get_current_config()
            
            if role_name in config:
                config[role_name] = cls._modules_to_strings(modules)
                
                if cls._save_config(config):
                    logger.info(f"Updated role '{role_name}' with modules: {[m.value for m in modules]}")
                    return True
                else:
                    logger.error(f"Failed to save configuration after updating role '{role_name}'")
                    return False
            else:
                logger.warning(f"Role '{role_name}' not found for update")
                return False
                
        except Exception as e:
            logger.error(f"Error updating role '{role_name}': {e}")
            return False
    
    @classmethod
    def remove_role(cls, role_name: str) -> bool:
        """
        Elimina un rol del mapeo (persistente)
        """
        try:
            # No permitir eliminar roles del sistema
            if role_name in cls._DEFAULT_ROLE_MODULES:
                logger.warning(f"Cannot remove system role '{role_name}'")
                return False
                
            config = cls._get_current_config()
            
            if role_name in config:
                del config[role_name]
                
                if cls._save_config(config):
                    logger.info(f"Removed role '{role_name}' from mapping")
                    return True
                else:
                    logger.error(f"Failed to save configuration after removing role '{role_name}'")
                    return False
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
        config = cls._get_current_config()
        configured_roles = set(config.keys())
        
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
                'name': cls._get_module_friendly_name(module),
                'value': module.value,
                'description': cls._get_module_description(module)
            }
            for module in Module
        }
    
    @classmethod
    def _get_module_friendly_name(cls, module: Module) -> str:
        """
        Obtiene nombre amigable del módulo
        """
        friendly_names = {
            Module.GEOGRAPHIC: "Módulo Geográfico",
            Module.CLIMATE_DATA: "Datos Climáticos",
            Module.CROP_DATA: "Datos de Cultivos",
            Module.STRESS_DATA: "Datos de Estreses",
            Module.PHENOLOGICAL_STAGE: "Etapas Fenológicas",
            Module.USER_MANAGEMENT: "Gestión de Usuarios",
            Module.CONFIGURATION: "Configuración",
        }
        return friendly_names.get(module, module.value)
    
    @classmethod
    def _get_module_description(cls, module: Module) -> str:
        """
        Obtiene descripción amigable del módulo
        """
        descriptions = {
            Module.GEOGRAPHIC: "Gestión de países, estados, municipios y localizaciones",
            Module.CLIMATE_DATA: "Gestión de datos climáticos",
            Module.CROP_DATA: "Gestión de datos de cultivos",
            Module.STRESS_DATA: "Gestión de datos de estreses",
            Module.PHENOLOGICAL_STAGE: "Gestión de etapas fenológicas",
            Module.USER_MANAGEMENT: "Administración de usuarios y roles del sistema",
            Module.CONFIGURATION: "Configuración de fuentes de datos",
        }
        return descriptions.get(module, module.value)