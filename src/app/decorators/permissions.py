from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user
from flask_babel import _
from app.config.permissions import Module, user_has_module_access
import logging

logger = logging.getLogger(__name__)

def require_module_access(module: Module, permission_type: str = 'read'):
    """
    Decorador que requiere acceso al módulo con un tipo específico de permiso
    
    Args:
        module: Módulo requerido
        permission_type: Tipo de permiso requerido ('create', 'read', 'update', 'delete')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash(_('Please log in to access this page.'), 'info')
                return redirect(url_for('main.login'))
            
            # Verificar acceso al módulo con el permiso específico
            if not user_has_module_access(module, permission_type):
                logger.warning(
                    f"User {current_user.username} denied {permission_type} access to module {module.value}"
                )
                flash(_('You do not have permission to access this module.'), 'error')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def check_module_access(module: Module, permission_type: str = 'read') -> bool:
    """
    Función auxiliar para verificar acceso a módulos en templates
    
    Args:
        module: Módulo a verificar
        permission_type: Tipo de permiso ('create', 'read', 'update', 'delete')
    
    Returns:
        True si el usuario tiene acceso
    """
    if not current_user.is_authenticated:
        return False
    
    return user_has_module_access(module, permission_type)