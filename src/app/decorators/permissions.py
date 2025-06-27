from functools import wraps
from flask import abort, flash, redirect, url_for, current_app
from flask_login import current_user
from flask_babel import _
from app.config.permissions import RolePermissionMapper, Module
import logging

logger = logging.getLogger(__name__)

def require_module_access(module: Module):
    """
    Decorador que requiere acceso al módulo (con permisos completos)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash(_('Please log in to access this page.'), 'info')
                return redirect(url_for('main.login'))
            
            # Obtener roles del usuario
            user_roles = getattr(current_user, 'roles', [])
            
            # Verificar acceso al módulo
            if not RolePermissionMapper.user_has_module_access(user_roles, module):
                logger.warning(f"User {current_user.username} denied access to module {module.value}")
                flash(_('You do not have access to this module.'), 'error')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def check_module_access(module: Module) -> bool:
    """
    Función auxiliar para verificar acceso a módulos en templates
    """
    if not current_user.is_authenticated:
        return False
    
    user_roles = getattr(current_user, 'roles', [])
    return RolePermissionMapper.user_has_module_access(user_roles, module)