from flask import Flask
from flask_login import LoginManager
from config import Config
from dotenv import load_dotenv
from aclimate_v3_orm.database.base import create_tables

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    load_dotenv()

    create_tables()
    
    # Inicializar extensiones
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    # Registrar rutas
    from app.routes.main_routes import bp as main_bp
    from app.routes.country_routes import bp as country_bp
    from app.routes.adm1_routes import bp as adm1_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(country_bp)
    app.register_blueprint(adm1_bp)
    
    return app