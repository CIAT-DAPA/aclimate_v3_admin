from typing import List, Dict, Optional
from datetime import datetime

class RoleService:
    """Servicio para manejar roles sin ORM"""
    
    def __init__(self):
        # Simulamos una base de datos en memoria
        self._roles = [
            {
                'id': 1,
                'name': 'Admin',
                'description': 'Administrador del sistema con acceso completo',
                'modules': {
                    'geographic': True,
                    'crops': True,
                    'weather': True,
                    'users': True,
                    'api': True,   
                },
                'enable': True,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            {
                'id': 2,
                'name': 'Geo Admin',
                'description': 'Usuario con acceso limitado a módulos geográficos',
                'modules': {
                    'geographic': True,
                    'crops': False,
                    'weather': False,
                    'users': False,
                    'api': False,   
                },
                'enable': True,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            {
                'id': 3,
                'name': 'Guest',
                'description': 'Invitado con acceso muy limitado',
                'modules': {
                    'geographic': False,
                    'crops': False,
                    'weather': False,
                    'users': False,
                    'api': False,   
                },
                'enable': True,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
        ]
        self._next_id = 4
    
    def get_all(self) -> List[Dict]:
        """Obtener todos los roles"""
        return self._roles.copy()
    
    def get_active_roles(self) -> List[Dict]:
        """Obtener solo los roles activos"""
        return [role.copy() for role in self._roles if role.get('enable', True)]
    
    def get_by_id(self, role_id: int) -> Optional[Dict]:
        """Obtener rol por ID"""
        for role in self._roles:
            if role['id'] == role_id:
                return role.copy()
        return None
    
    def get_by_name(self, name: str) -> Optional[Dict]:
        """Obtener rol por nombre"""
        for role in self._roles:
            if role['name'].lower() == name.lower():
                return role.copy()
        return None
    
    def create(self, role_data: Dict) -> Dict:
        """Crear nuevo rol"""
        # Verificar si ya existe un rol con ese nombre
        if self.get_by_name(role_data['name']):
            raise ValueError(f"Ya existe un rol con el nombre '{role_data['name']}'")
        
        # Módulos por defecto (todos deshabilitados)
        default_modules = {
            'geographic': False,
            'crops': False,
            'weather': False,
            'users': False,
            'api': False,
        }
        
        new_role = {
            'id': self._next_id,
            'name': role_data['name'],
            'description': role_data.get('description', ''),
            'modules': role_data.get('modules', default_modules),
            'enable': role_data.get('enable', True),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        self._roles.append(new_role)
        self._next_id += 1
        
        return new_role.copy()
    
    def update(self, role_id: int, role_data: Dict) -> Optional[Dict]:
        """Actualizar rol existente"""
        for i, role in enumerate(self._roles):
            if role['id'] == role_id:
                # Verificar si el nuevo nombre ya existe en otro rol
                if 'name' in role_data and role_data['name'] != role['name']:
                    existing = self.get_by_name(role_data['name'])
                    if existing and existing['id'] != role_id:
                        raise ValueError(f"Ya existe un rol con el nombre '{role_data['name']}'")
                
                # Actualizar campos
                if 'name' in role_data:
                    self._roles[i]['name'] = role_data['name']
                if 'description' in role_data:
                    self._roles[i]['description'] = role_data['description']
                if 'modules' in role_data:
                    self._roles[i]['modules'] = role_data['modules']
                if 'enable' in role_data:
                    self._roles[i]['enable'] = role_data['enable']
                
                self._roles[i]['updated_at'] = datetime.now()
                
                return self._roles[i].copy()
        
        return None
    
    def update_module_access(self, role_id: int, module_name: str, access: bool) -> Optional[Dict]:
        """Actualizar acceso a un módulo específico"""
        for i, role in enumerate(self._roles):
            if role['id'] == role_id:
                if module_name in role['modules']:
                    self._roles[i]['modules'][module_name] = access
                    self._roles[i]['updated_at'] = datetime.now()
                    return self._roles[i].copy()
                else:
                    raise ValueError(f"El módulo '{module_name}' no existe")
        return None
    
    def delete(self, role_id: int) -> bool:
        """Deshabilitar rol (soft delete)"""
        for i, role in enumerate(self._roles):
            if role['id'] == role_id:
                self._roles[i]['enable'] = False
                self._roles[i]['updated_at'] = datetime.now()
                return True
        return False
    
    def hard_delete(self, role_id: int) -> bool:
        """Eliminar rol permanentemente"""
        for i, role in enumerate(self._roles):
            if role['id'] == role_id:
                del self._roles[i]
                return True
        return False
    
    def restore(self, role_id: int) -> bool:
        """Restaurar rol deshabilitado"""
        for i, role in enumerate(self._roles):
            if role['id'] == role_id:
                self._roles[i]['enable'] = True
                self._roles[i]['updated_at'] = datetime.now()
                return True
        return False
    
    def get_available_modules(self) -> List[str]:
        """Obtener lista de módulos disponibles"""
        return ['geographic', 'crops', 'weather', 'users', 'api']
    
    def has_module_access(self, role_id: int, module_name: str) -> bool:
        """Verificar si un rol tiene acceso a un módulo específico"""
        role = self.get_by_id(role_id)
        if role and role.get('enable', True):
            return role.get('modules', {}).get(module_name, False)
        return False
    
    def get_role_modules(self, role_id: int) -> Dict[str, bool]:
        """Obtener todos los módulos de un rol"""
        role = self.get_by_id(role_id)
        if role:
            return role.get('modules', {})
        return {}
    
    def get_roles_with_module_access(self, module_name: str) -> List[Dict]:
        """Obtener todos los roles que tienen acceso a un módulo específico"""
        roles_with_access = []
        for role in self._roles:
            if role.get('enable', True) and role.get('modules', {}).get(module_name, False):
                roles_with_access.append(role.copy())
        return roles_with_access