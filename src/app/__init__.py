from flask import Flask, request, session
from flask_login import LoginManager
from flask_babel import Babel
from config import Config
from dotenv import load_dotenv
from aclimate_v3_orm.database.base import create_tables

login_manager = LoginManager()
babel = Babel()

def get_locale():
    # 1. Si hay idioma en la sesión, usarlo
    if 'language' in session and session['language'] in Config.LANGUAGES:
        return session['language']
    
    # 2. Si no, usar el mejor idioma basado en Accept-Language del navegador
    requested = request.accept_languages.best_match(Config.LANGUAGES.keys())
    if requested:
        return requested
    
    # 3. Si no se encuentra coincidencia, usar el idioma por defecto
    return Config.BABEL_DEFAULT_LOCALE


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    load_dotenv()

    create_tables()
    
    # Inicializar extensiones
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'

    # Inicializar Babel
    babel.init_app(app, locale_selector=get_locale)
    
    # Hacer get_locale disponible en templates
    @app.context_processor
    def inject_conf_vars():
        current_locale = get_locale()
        # Asegurar que el locale actual existe en LANGUAGES
        if current_locale not in Config.LANGUAGES:
            current_locale = Config.BABEL_DEFAULT_LOCALE
            
        return {
            'get_locale': lambda: current_locale,
            'config': Config
        }
    
    # Registrar rutas
    from app.routes.main_routes import bp as main_bp
    from app.routes.country_routes import bp as country_bp
    from app.routes.adm1_routes import bp as adm1_bp
    from app.routes.adm2_routes import bp as adm2_bp
    from app.routes.role_routes import bp as role_bp
    from app.routes.language_routes import bp as language_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(country_bp)
    app.register_blueprint(adm1_bp)
    app.register_blueprint(adm2_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(language_bp)

    return app