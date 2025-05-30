import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuración de PostgreSQL (para más adelante)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

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