from enum import Enum
from typing import List, Dict
import logging
from flask_login import current_user

logger = logging.getLogger(__name__)

class Module(Enum):
    """Módulos disponibles en la aplicación - debe coincidir con el enum en ORM"""
    GEOGRAPHIC = "geographic"
    CLIMATE_DATA = "climate_data"
    CROP_DATA = "crop_data"
    INDICATORS_DATA = "indicators_data"
    STRESS_DATA = "stress_data"
    PHENOLOGICAL_STAGE = "phenological_stage"
    USER_MANAGEMENT = "user_management"
    CONFIGURATION = "configuration"


# Información de los módulos con nombres y descripciones
MODULES_INFO: Dict[str, Dict[str, str]] = {
    "geographic": {
        "name": "Datos Geográficos",
        "description": "Gestión de países, regiones administrativas (ADM1, ADM2) y localizaciones"
    },
    "climate_data": {
        "name": "Datos Climáticos",
        "description": "Administración de datos y variables climáticas"
    },
    "crop_data": {
        "name": "Datos de Cultivos",
        "description": "Gestión de cultivos, cultivares, temporadas y tipos de suelo"
    },
    "indicators_data": {
        "name": "Indicadores",
        "description": "Administración de indicadores, categorías y asociaciones por país"
    },
    "stress_data": {
        "name": "Datos de Estreses",
        "description": "Gestión de estreses abióticos y bióticos"
    },
    "phenological_stage": {
        "name": "Etapas Fenológicas",
        "description": "Administración de etapas del desarrollo de cultivos"
    },
    "user_management": {
        "name": "Gestión de Usuarios",
        "description": "Administración de usuarios, roles y permisos del sistema"
    },
    "configuration": {
        "name": "Configuración",
        "description": "Configuración del sistema, fuentes de datos y parámetros generales"
    }
}


def get_modules_info() -> Dict[str, Dict[str, str]]:
    """
    Obtiene la información completa de todos los módulos
    
    Returns:
        Diccionario con información de módulos (nombre y descripción)
    """
    return MODULES_INFO


def get_module_info(module_value: str) -> Dict[str, str]:
    """
    Obtiene la información de un módulo específico
    
    Args:
        module_value: Valor del módulo (ej: "geographic")
    
    Returns:
        Diccionario con nombre y descripción del módulo
    """
    return MODULES_INFO.get(module_value, {"name": module_value, "description": ""})


def user_has_module_access(module: Module, permission_type: str = 'read') -> bool:
    """
    Verifica si el usuario actual tiene acceso a un módulo específico
    
    Args:
        module: Módulo a verificar
        permission_type: Tipo de permiso ('create', 'read', 'update', 'delete')
    
    Returns:
        True si el usuario tiene el permiso especificado para el módulo
    """
    if not current_user.is_authenticated:
        return False
    
    return current_user.has_module_access(module.value, permission_type)


def get_user_accessible_modules() -> List[str]:
    """
    Obtiene la lista de módulos accesibles para el usuario actual
    
    Returns:
        Lista de nombres de módulos (valores del enum)
    """
    if not current_user.is_authenticated:
        return []
    
    return current_user.get_accessible_modules()


def check_module_permission(module: Module, permission_type: str = 'read') -> bool:
    """
    Función auxiliar para verificar permisos en templates y código
    
    Args:
        module: Módulo a verificar
        permission_type: Tipo de permiso
    
    Returns:
        True si tiene el permiso
    """
    return user_has_module_access(module, permission_type)
