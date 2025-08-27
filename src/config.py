import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuración de PostgreSQL (para más adelante)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración de la API
    API_BASE_URL = os.environ.get('API_BASE_URL') or 'http://127.0.0.1:8000'

    # Configuración de internacionalización
    LANGUAGES = {
        'es_CO': {
            'name': 'Español Colombia'
        },
        'es_GT':{
            'name': 'Español Guatemala'
        },
        'en_US': {
            'name': 'English United States'
        }
    }
    
    # Idioma por defecto
    BABEL_DEFAULT_LOCALE = 'es_CO'
    BABEL_DEFAULT_TIMEZONE = 'UTC'

     # Keycloak OAuth Configuration
    KEYCLOAK_SERVER_URL = os.environ.get('KEYCLOAK_SERVER_URL', 'http://localhost:8080')
    KEYCLOAK_REALM = os.environ.get('KEYCLOAK_REALM', 'aclimate')
    KEYCLOAK_CLIENT_ID = os.environ.get('KEYCLOAK_CLIENT_ID', 'aclimate_admin')
    KEYCLOAK_CLIENT_SECRET = os.environ.get('KEYCLOAK_CLIENT_SECRET', 'your-client-secret')
    
    # OAuth URLs
    @property
    def KEYCLOAK_AUTHORIZATION_URL(self):
        return f"{self.KEYCLOAK_SERVER_URL}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/auth"
    
    @property
    def KEYCLOAK_TOKEN_URL(self):
        return f"{self.KEYCLOAK_SERVER_URL}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/token"
    
    @property
    def KEYCLOAK_USERINFO_URL(self):
        return f"{self.KEYCLOAK_SERVER_URL}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/userinfo"
    
    @property
    def KEYCLOAK_LOGOUT_URL(self):
        return f"{self.KEYCLOAK_SERVER_URL}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/logout"
    
    # Define which models are compatible with which crops
    MODELS_AND_CROPS = {
        'DSSAT': {"Maize", "Wheat"},
        'ORYZA': {"Rice"}
    }

    # Configurar carpeta para subidas
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'conf_files')
