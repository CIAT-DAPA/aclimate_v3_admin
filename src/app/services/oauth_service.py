from authlib.integrations.flask_client import OAuth
from flask import current_app, session, url_for, redirect
from typing import Optional, Dict
import requests
import logging

logger = logging.getLogger(__name__)

class OAuthService:
    """Servicio para manejar autenticación OAuth con Keycloak"""
    
    def __init__(self, app=None):
        self.oauth = OAuth()
        self.keycloak = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar OAuth con la aplicación Flask"""
        try:
            self.oauth.init_app(app)
            
            # Log de configuración
            logger.info(f"Initializing Keycloak OAuth client:")
            logger.info(f"  Server URL: {app.config['KEYCLOAK_SERVER_URL']}")
            logger.info(f"  Realm: {app.config['KEYCLOAK_REALM']}")
            logger.info(f"  Client ID: {app.config['KEYCLOAK_CLIENT_ID']}")
            
            # Configurar endpoints manualmente basado en tu URL funcional
            base_url = f"{app.config['KEYCLOAK_SERVER_URL']}/realms/{app.config['KEYCLOAK_REALM']}"
            
            # URLs de Keycloak 18+ (sin /auth)
            authorization_endpoint = f"{base_url}/protocol/openid-connect/auth"
            token_endpoint = f"{base_url}/protocol/openid-connect/token"
            userinfo_endpoint = f"{base_url}/protocol/openid-connect/userinfo"
            jwks_uri = f"{base_url}/protocol/openid-connect/certs"
            issuer = base_url
            
            logger.info(f"  Authorization endpoint: {authorization_endpoint}")
            logger.info(f"  Token endpoint: {token_endpoint}")
            logger.info(f"  Userinfo endpoint: {userinfo_endpoint}")
            logger.info(f"  JWKS URI: {jwks_uri}")
            
            # Configurar cliente Keycloak con endpoints manuales
            self.keycloak = self.oauth.register(
                name='keycloak',
                client_id=app.config['KEYCLOAK_CLIENT_ID'],
                client_secret=app.config['KEYCLOAK_CLIENT_SECRET'],
                authorize_url=authorization_endpoint,
                access_token_url=token_endpoint,
                userinfo_endpoint=userinfo_endpoint,
                jwks_uri=jwks_uri,
                issuer=issuer,
                client_kwargs={
                    'scope': 'openid email profile',
                    'response_type': 'code',
                    'token_endpoint_auth_method': 'client_secret_post'
                }
            )
            
            if self.keycloak:
                logger.info("Keycloak OAuth client initialized successfully")
            else:
                logger.error("Failed to initialize Keycloak OAuth client")
                
        except Exception as e:
            logger.error(f"Error initializing OAuth service: {e}")
            self.keycloak = None
    
    def get_authorization_url(self, redirect_uri: str):
        """Obtener URL de autorización para redirigir al usuario"""
        if not self.keycloak:
            logger.error("Keycloak client not initialized")
            raise RuntimeError("OAuth service not properly initialized")
        
        try:
            logger.info(f"Redirecting to authorization URL with callback: {redirect_uri}")
            return self.keycloak.authorize_redirect(redirect_uri)
        except Exception as e:
            logger.error(f"Error getting authorization URL: {e}")
            raise
    
    def exchange_code_for_token(self) -> Optional[Dict]:
        """Intercambiar código de autorización por token"""
        if not self.keycloak:
            logger.error("Keycloak client not initialized")
            return None
            
        try:
            logger.info("Attempting to exchange authorization code for token")
            token = self.keycloak.authorize_access_token()
            logger.info("Successfully exchanged code for token")
            logger.debug(f"Token keys: {list(token.keys()) if token else 'None'}")
            return token
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            return None
    
    def get_user_info(self, token: Dict) -> Optional[Dict]:
        """Obtener información del usuario usando el token"""
        if not self.keycloak:
            logger.error("Keycloak client not initialized")
            return None
            
        try:
            logger.info("Attempting to get user info")
            logger.debug(f"Token structure: {list(token.keys()) if token else 'None'}")
            
            # Método 1: Intentar con userinfo endpoint usando Authlib
            try:
                user_info = self.keycloak.userinfo(token=token)
                if user_info:
                    logger.info(f"Successfully retrieved user info via Authlib: {user_info.get('preferred_username', 'unknown')}")
                    return user_info
            except Exception as e:
                logger.warning(f"Authlib userinfo failed: {e}")
            
            # Método 2: Intentar con requests directo
            if 'access_token' in token:
                userinfo_url = f"{current_app.config['KEYCLOAK_SERVER_URL']}/realms/{current_app.config['KEYCLOAK_REALM']}/protocol/openid-connect/userinfo"
                
                response = requests.get(
                    userinfo_url,
                    headers={'Authorization': f"Bearer {token['access_token']}"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    user_info = response.json()
                    logger.info(f"Successfully retrieved user info from userinfo endpoint: {user_info.get('preferred_username', 'unknown')}")
                    return user_info
                else:
                    logger.warning(f"Userinfo endpoint returned status {response.status_code}: {response.text}")
            
            # Método 3: Fallback - parsear ID token
            if 'id_token' in token:
                try:
                    user_info = self.keycloak.parse_id_token(token)
                    logger.info(f"Successfully parsed ID token: {user_info.get('preferred_username', 'unknown')}")
                    return user_info
                except Exception as e:
                    logger.warning(f"Failed to parse ID token: {e}")
            
            logger.error("Could not retrieve user info from any method")
            return None
            
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None
    
    def validate_token(self, access_token: str) -> bool:
        """Validar que el token siga siendo válido"""
        try:
            userinfo_url = f"{current_app.config['KEYCLOAK_SERVER_URL']}/realms/{current_app.config['KEYCLOAK_REALM']}/protocol/openid-connect/userinfo"
            
            response = requests.get(
                userinfo_url,
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return False
    
    def logout_url(self, redirect_uri: str = None, id_token: str = None) -> str:
        """Obtener URL de logout de Keycloak con id_token_hint"""
        logout_url = f"{current_app.config['KEYCLOAK_SERVER_URL']}/realms/{current_app.config['KEYCLOAK_REALM']}/protocol/openid-connect/logout"
        
        params = []

        # Agregar id_token_hint si está disponible
        if id_token:
            params.append(f"id_token_hint={id_token}")

        # Agregar redirect_uri si está disponible
        if redirect_uri:
            params.append(f"post_logout_redirect_uri={redirect_uri}")
        
        if params:
            logout_url += "?" + "&".join(params)
        
        logger.info(f"Generated logout URL: {logout_url}")
        return logout_url
    
    @staticmethod
    def get_auth_headers(token: str = None) -> Dict[str, str]:
        """Retorna headers de autenticación para peticiones a la API"""
        if not token:
            token = session.get('access_token')
        
        if token:
            return {'Authorization': f'Bearer {token}'}
        return {}