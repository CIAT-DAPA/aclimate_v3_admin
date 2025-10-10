import logging
from flask_login import UserMixin
from flask import session
from typing import List, Optional, Dict
from aclimate_v3_orm.services.user_service import UserService as ORMUserService
from aclimate_v3_orm.services.user_access_service import UserAccessService
from aclimate_v3_orm.services.role_service import RoleService
from aclimate_v3_orm.schemas import UserRead, UserAccessRead, RoleRead

logger = logging.getLogger(__name__)

class User(UserMixin):
    """User model integrating Keycloak authentication with ORM database"""
    
    def __init__(self, keycloak_user_data: Dict, db_user: Optional[UserRead] = None):
        """
        Initialize user from Keycloak data and optionally from database
        
        Args:
            keycloak_user_data: User info from Keycloak OAuth
            db_user: User data from ORM database (if available)
        """
        # Basic Keycloak info
        self.keycloak_id = (keycloak_user_data.get('sub') or 
                           keycloak_user_data.get('id'))
        self.username = (keycloak_user_data.get('preferred_username') or 
                        keycloak_user_data.get('username') or 
                        keycloak_user_data.get('email', '').split('@')[0])
        self.email = keycloak_user_data.get('email', '')
        self.first_name = keycloak_user_data.get('given_name', '')
        self.last_name = keycloak_user_data.get('family_name', '')
        self.name = keycloak_user_data.get('name', f"{self.first_name} {self.last_name}".strip())
        
        # Database info
        self.db_id = None
        self.role_id = None
        self.role_name = None
        self.role_app = None
        self.user_accesses = []
        self.countries = []
        
        # Load from database if available
        if db_user:
            self._load_from_db(db_user)
        
        logger.info(f"Created user: {self.username} (Keycloak ID: {self.keycloak_id}, DB ID: {self.db_id})")
        logger.info(f"  Role: {self.role_name}, Countries: {[c['name'] for c in self.countries]}")
    
    def _load_from_db(self, db_user: UserRead):
        """Load user data from ORM database"""
        try:
            self.db_id = db_user.id
            self.role_id = db_user.role_id
            
            # Load role information
            if db_user.role:
                self.role_name = db_user.role.name
                self.role_app = db_user.role.app.value if db_user.role.app else None
            
            # Load user accesses (countries and permissions)
            if db_user.accesses:
                self.user_accesses = [
                    {
                        'user_id': access.user_id,
                        'country_id': access.country_id,
                        'country_name': access.country.name if access.country else None,
                        'role_id': access.role_id,
                        'role_name': access.role.name if access.role else None,
                        'create': access.create,
                        'read': access.read,
                        'update': access.update,
                        'delete': access.delete,
                        # Note: module field should be added to UserAccess model in ORM
                        'module': getattr(access, 'module', None).value if hasattr(access, 'module') and getattr(access, 'module', None) else None
                    }
                    for access in db_user.accesses
                ]
                
                # Extract unique countries
                countries_dict = {}
                for access in self.user_accesses:
                    country_id = access['country_id']
                    if country_id and country_id not in countries_dict:
                        countries_dict[country_id] = {
                            'id': country_id,
                            'name': access['country_name'],
                            'display_name': access['country_name']
                        }
                self.countries = list(countries_dict.values())
            
            logger.info(f"Loaded user from DB: ID={self.db_id}, Role={self.role_name}, Accesses={len(self.user_accesses)}")
            
        except Exception as e:
            logger.error(f"Error loading user data from database: {e}")
    
    def get_id(self):
        """Return user ID for Flask-Login (use Keycloak ID)"""
        return str(self.keycloak_id)
    
    def has_module_access(self, module_value: str, permission_type: str = 'read') -> bool:
        """
        Check if user has access to a specific module with a specific permission
        
        Args:
            module_value: Module enum value (e.g., 'geographic', 'GEOGRAPHIC', 'crop_data', 'CROP_DATA')
            permission_type: Type of permission ('create', 'read', 'update', 'delete')
        
        Returns:
            True if user has the specified permission for the module
        """
        # Convertir a mayúsculas para comparación case-insensitive
        module_value_upper = module_value.upper()
        for access in self.user_accesses:
            if access.get('module', '').upper() == module_value_upper:
                return access.get(permission_type, False)
        return False
    
    def has_country_access(self, country_id: int) -> bool:
        """Check if user has access to a specific country"""
        return any(access['country_id'] == country_id for access in self.user_accesses)
    
    def get_accessible_countries(self) -> List[Dict]:
        """Get list of countries user has access to"""
        return self.countries
    
    def get_country_ids(self) -> List[int]:
        """Get list of country IDs user has access to"""
        return [country['id'] for country in self.countries]
    
    def get_permissions_for_module(self, module_value: str) -> Dict[str, bool]:
        """
        Get all permissions for a specific module
        
        Returns:
            Dict with 'create', 'read', 'update', 'delete' permissions
        """
        # Convertir a mayúsculas para comparación case-insensitive
        module_value_upper = module_value.upper()
        for access in self.user_accesses:
            if access.get('module', '').upper() == module_value_upper:
                return {
                    'create': access.get('create', False),
                    'read': access.get('read', False),
                    'update': access.get('update', False),
                    'delete': access.get('delete', False)
                }
        return {'create': False, 'read': False, 'update': False, 'delete': False}
    
    def get_accessible_modules(self) -> List[str]:
        """Get list of modules user has at least read access to"""
        modules = set()
        for access in self.user_accesses:
            module = access.get('module')
            if module and access.get('read', False):
                modules.add(module)
        return list(modules)
    
    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.role_name in ['admin', 'adminsuper'] if self.role_name else False
    
    def is_super_admin(self) -> bool:
        """Check if user has super admin role"""
        return self.role_name == 'adminsuper' if self.role_name else False
    
    @property
    def role(self):
        """Compatibility: return role name"""
        return self.role_name or 'guest'
    
    @property
    def roles(self):
        """Compatibility: return roles as list"""
        return [self.role_name] if self.role_name else []
    
    @staticmethod
    def get(user_id):
        """Load user from session by Keycloak ID"""
        user_data = session.get('user_data')
        if user_data:
            keycloak_id = (user_data.get('sub') or user_data.get('id'))
            if str(keycloak_id) == str(user_id):
                # Reload from database to get fresh data
                try:
                    orm_user_service = ORMUserService()
                    db_users = orm_user_service.get_by_keycloak_ext_id(keycloak_id)
                    db_user = db_users[0] if db_users else None
                    return User(user_data, db_user)
                except Exception as e:
                    logger.error(f"Error loading user from database: {e}")
                    # Return user with Keycloak data only
                    return User(user_data, None)
        return None
    
    @staticmethod
    def authenticate_oauth(token_data, user_info):
        """Authenticate user with OAuth and load from database"""
        if token_data and user_info:
            # Save tokens in session
            session['access_token'] = token_data.get('access_token')
            session['refresh_token'] = token_data.get('refresh_token')
            session['id_token'] = token_data.get('id_token')
            session['user_data'] = user_info
            
            keycloak_id = user_info.get('sub')
            
            logger.info(f"Authenticating user via OAuth: {user_info.get('preferred_username', 'unknown')}")
            
            # Try to load user from database
            db_user = None
            try:
                orm_user_service = ORMUserService()
                db_users = orm_user_service.get_by_keycloak_ext_id(keycloak_id)
                
                if db_users:
                    db_user = db_users[0]
                    logger.info(f"User found in database: ID={db_user.id}")
                else:
                    logger.warning(f"User with Keycloak ID {keycloak_id} not found in database")
                    
            except Exception as e:
                logger.error(f"Error loading user from database: {e}")
            
            # Create user object
            user = User(user_info, db_user)
            
            return user
        return None
    
    def validate_token(self):
        """Validate that the user's token is still valid"""
        access_token = session.get('access_token')
        if not access_token:
            logger.warning("No access token found in session")
            return False
        
        from app.services.oauth_service import OAuthService
        oauth_service = OAuthService()
        is_valid = oauth_service.validate_token(access_token)
        
        if not is_valid:
            logger.warning(f"Token validation failed for user: {self.username}")
        
        return is_valid
    
    def reload_from_db(self):
        """Reload user data from database"""
        try:
            orm_user_service = ORMUserService()
            db_users = orm_user_service.get_by_keycloak_ext_id(self.keycloak_id)
            
            if db_users:
                self._load_from_db(db_users[0])
                # Update session
                session['user_data_refreshed'] = True
                logger.info(f"Successfully reloaded user data from database")
                return True
            else:
                logger.warning(f"User not found in database during reload")
                return False
                
        except Exception as e:
            logger.error(f"Error reloading user from database: {e}")
            return False
    
    # Compatibility methods
    def check_password(self, password):
        """Compatibility: OAuth doesn't use local passwords"""
        return False
    
    def refresh_roles_and_countries(self):
        """Compatibility: reload from database"""
        return self.reload_from_db()
    
    def refresh_roles(self):
        """Compatibility: reload from database"""
        return self.reload_from_db()
    
    def get_country_names(self):
        """Get list of country names"""
        return [country['name'] for country in self.countries]
    
    def get_country_group_names(self):
        """Compatibility: get country names"""
        return self.get_country_names()
    
    def has_group_access(self, group_name: str) -> bool:
        """Compatibility: check country access by name"""
        return any(country['name'].lower() == group_name.lower() for country in self.countries)
    def is_super_admin(self):
        """Verifica si el usuario es super administrador"""
        return 'adminsuper' in self.roles
    
    def is_super_admin(self):
        """Check if user has super admin role"""
        return self.role_name == 'adminsuper' if self.role_name else False
    
    @property
    def role(self):
        """Compatibility: return role name"""
        return self.role_name or 'guest'
    
    @property
    def roles(self):
        """Compatibility: return roles as list"""
        return [self.role_name] if self.role_name else []
    
    @staticmethod
    def get(user_id):
        """Load user from session by Keycloak ID"""
        user_data = session.get('user_data')
        if user_data:
            keycloak_id = (user_data.get('sub') or user_data.get('id'))
            if str(keycloak_id) == str(user_id):
                # Reload from database to get fresh data
                try:
                    orm_user_service = ORMUserService()
                    db_users = orm_user_service.get_by_keycloak_ext_id(keycloak_id)
                    db_user = db_users[0] if db_users else None
                    return User(user_data, db_user)
                except Exception as e:
                    logger.error(f"Error loading user from database: {e}")
                    # Return user with Keycloak data only
                    return User(user_data, None)
        return None
    
    @staticmethod
    def authenticate_oauth(token_data, user_info):
        """Authenticate user with OAuth and load from database"""
        if token_data and user_info:
            # Save tokens in session
            session['access_token'] = token_data.get('access_token')
            session['refresh_token'] = token_data.get('refresh_token')
            session['id_token'] = token_data.get('id_token')
            session['user_data'] = user_info
            
            keycloak_id = user_info.get('sub')
            
            logger.info(f"Authenticating user via OAuth: {user_info.get('preferred_username', 'unknown')}")
            
            # Try to load user from database
            db_user = None
            try:
                orm_user_service = ORMUserService()
                db_users = orm_user_service.get_by_keycloak_ext_id(keycloak_id)
                
                if db_users:
                    db_user = db_users[0]
                    logger.info(f"User found in database: ID={db_user.id}")
                else:
                    logger.warning(f"User with Keycloak ID {keycloak_id} not found in database")
                    
            except Exception as e:
                logger.error(f"Error loading user from database: {e}")
            
            # Create user object
            user = User(user_info, db_user)
            
            return user
        return None
    
    def validate_token(self):
        """Validate that the user's token is still valid"""
        access_token = session.get('access_token')
        if not access_token:
            logger.warning("No access token found in session")
            return False
        
        from app.services.oauth_service import OAuthService
        oauth_service = OAuthService()
        is_valid = oauth_service.validate_token(access_token)
        
        if not is_valid:
            logger.warning(f"Token validation failed for user: {self.username}")
        
        return is_valid
    
    def reload_from_db(self):
        """Reload user data from database"""
        try:
            orm_user_service = ORMUserService()
            db_users = orm_user_service.get_by_keycloak_ext_id(self.keycloak_id)
            
            if db_users:
                self._load_from_db(db_users[0])
                # Update session
                session['user_data_refreshed'] = True
                logger.info(f"Successfully reloaded user data from database")
                return True
            else:
                logger.warning(f"User not found in database during reload")
                return False
                
        except Exception as e:
            logger.error(f"Error reloading user from database: {e}")
            return False
    
    # Compatibility methods
    def check_password(self, password):
        """Compatibility: OAuth doesn't use local passwords"""
        return False
    
    def refresh_roles_and_countries(self):
        """Compatibility: reload from database"""
        return self.reload_from_db()
    
    def refresh_roles(self):
        """Compatibility: reload from database"""
        return self.reload_from_db()
    
    def get_country_names(self):
        """Get list of country names"""
        return [country['name'] for country in self.countries]
    
    def get_country_group_names(self):
        """Compatibility: get country names"""
        return self.get_country_names()
    
    def has_group_access(self, group_name: str) -> bool:
        """Compatibility: check country access by name"""
        return any(country['name'].lower() == group_name.lower() for country in self.countries)