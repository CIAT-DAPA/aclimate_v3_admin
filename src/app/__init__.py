import os
from flask import Flask, app, request, session
from flask_login import LoginManager, current_user
from flask_babel import Babel 
from app.config.permissions import Module
from app.decorators.permissions import check_module_access
from config import Config
from app.services.oauth_service import OAuthService
from aclimate_v3_orm.database.base import create_tables
import logging

login_manager = LoginManager()
babel = Babel()
oauth_service = OAuthService()

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

    # Crear directorio de subidas si no existe
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER)

    print(f"App config DATABASE_URL: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

    create_tables()
    
    logging.basicConfig(level=logging.INFO)

    # Inicializar extensiones
    login_manager.init_app(app)
    oauth_service.init_app(app)
    babel.init_app(app, locale_selector=get_locale)

    # Store OAuth service in app extensions for access in routes
    app.extensions['oauth_service'] = oauth_service

    # Configure Flask-Login
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    # AGREGAR LOS FILTROS PERSONALIZADOS AQUÍ
    @app.template_filter('get_country_code')
    def get_country_code(country_name):
        """Convierte nombre de país a código ISO de 2 letras para flag-icons"""
        country_codes = {
            'colombia': 'co',
            'peru': 'pe',
            'brasil': 'br',
            'brazil': 'br',
            'ecuador': 'ec',
            'argentina': 'ar',
            'chile': 'cl',
            'bolivia': 'bo',
            'venezuela': 've',
            'uruguay': 'uy',
            'paraguay': 'py',
            'guyana': 'gy',
            'suriname': 'sr',
            'guatemala': 'gt',
            'nicaragua': 'ni',
            'honduras': 'hn',
            'costa rica': 'cr',
            'panama': 'pa',
            'mexico': 'mx',
            'estados unidos': 'us',
            'united states': 'us',
            'canada': 'ca',
            'españa': 'es',
            'spain': 'es',
        }
        
        if not country_name:
            return 'xx'  # Bandera genérica
        
        country_lower = country_name.lower().strip()
        return country_codes.get(country_lower, 'xx')

    @app.template_filter('get_country_flag')
    def get_country_flag(country_name):
        """Convierte nombre de país a emoji de bandera (respaldo)"""
        # Este filtro ahora es un respaldo, pero podemos mantenerlo
        return get_country_code(country_name)
    
    # Hacer get_locale disponible en templates
    @app.context_processor
    def inject_conf_vars():
        current_locale = get_locale()
        # Asegurar que el locale actual existe en LANGUAGES
        if current_locale not in Config.LANGUAGES:
            current_locale = Config.BABEL_DEFAULT_LOCALE
        
        return {
            'check_module_access': check_module_access,
            'Module': Module,
            'get_locale': lambda: current_locale,
            'config': Config
        }
    
    # Registrar rutas
    from app.routes.main_routes import bp as main_bp
    from app.routes.country_routes import bp as country_bp
    from app.routes.adm1_routes import bp as adm1_bp
    from app.routes.adm2_routes import bp as adm2_bp
    from app.routes.source_routes import bp as source_bp
    from app.routes.data_source_routes import bp as data_source_bp
    from app.routes.location_routes import bp as location_bp
    from app.routes.role_routes import bp as role_bp
    from app.routes.user_routes import bp as user_bp
    from app.routes.language_routes import bp as language_bp
    from app.routes.crop_routes import bp as crop_bp
    from app.routes.stress_routes import bp as stress_bp
    from app.routes.phenological_stage_routes import bp as phenological_stage_bp
    from app.routes.indicators_routes import bp as indicator_bp
    from app.routes.phenological_stage_stress_routes import bp as phenological_stage_stress_bp
    from app.routes.setup_routes import bp as setup_bp
    from app.routes.soil_routes import bp as soil_bp
    from app.routes.cultivar_routes import bp as cultivar_bp
    from app.routes.season_routes import bp as season_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(country_bp)
    app.register_blueprint(adm1_bp)
    app.register_blueprint(adm2_bp)
    app.register_blueprint(source_bp)
    app.register_blueprint(data_source_bp)
    app.register_blueprint(location_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(language_bp)
    app.register_blueprint(crop_bp)
    app.register_blueprint(stress_bp)
    app.register_blueprint(phenological_stage_bp)
    app.register_blueprint(indicator_bp)
    app.register_blueprint(phenological_stage_stress_bp)
    app.register_blueprint(setup_bp)
    app.register_blueprint(soil_bp)
    app.register_blueprint(cultivar_bp)
    app.register_blueprint(season_bp)

    return app