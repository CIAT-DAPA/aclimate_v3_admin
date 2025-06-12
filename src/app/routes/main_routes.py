from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from app.forms.login_form import LoginForm
from app.forms.register_form import RegisterForm
from app.models import User
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.role_service import RoleService
from app import login_manager
from app.decorators import token_required

bp = Blueprint('main', __name__)

# Instanciar servicios
auth_service = AuthService()
user_service = UserService()
role_service = RoleService()

@login_manager.user_loader
def load_user(user_id):
    """Carga el usuario desde la sesión"""
    return User.get(user_id)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return redirect(url_for('main.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if request.method == 'POST':
        username = form.username.data.strip() if form.username.data else ''
        password = form.password.data if form.password.data else ''
        
        # Validación manual en el servidor
        errors = {}
        if not username:
            errors['username'] = _('Username is required')
        elif len(username) < 3:
            errors['username'] = _('Username must be at least 3 characters')
        
        if not password:
            errors['password'] = _('Password is required')
        
        # Si no hay errores de validación, verificar credenciales
        if not errors:
            user = User.authenticate(username, password)
            if user:
                login_user(user)
                flash(_('Login successful!'), 'success')
                return redirect(url_for('main.home'))
            else:
                flash(_('Invalid username and/or password'), 'error')
        else:
            # Agregar errores al formulario para mostrar en el template
            if 'username' in errors:
                form.username.errors = [errors['username']]
            if 'password' in errors:
                form.password.errors = [errors['password']]
    
    return render_template('login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Ruta para registrar nuevos usuarios"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        try:
            user_service.create(
                username=form.username.data,
                email=form.email.data,
                name=form.name.data,
                last_name=form.last_name.data,
                password=form.password.data
            )

            flash(_('User registered successfully! Please login with your credentials.'), 'success')
            return redirect(url_for('main.login'))
            
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(_('Error registering user: {}').format(str(e)), 'danger')
    
    return render_template('register.html', form=form)

@bp.route('/logout')
@token_required
def logout():
    # Realizar logout en la API si es posible
    token = session.get('access_token')
    if token:
        AuthService.logout(token)
    
    # Limpiar la sesión local
    session.pop('access_token', None)
    session.pop('user_data', None)
    
    logout_user()
    flash(_('You have logged out successfully'), 'info')
    return redirect(url_for('main.login'))

@bp.route('/home')
@token_required
def home():
    return render_template('home.html')