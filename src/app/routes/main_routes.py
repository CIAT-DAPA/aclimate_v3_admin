from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.forms.login_form import LoginForm
from app.models import User
from app import login_manager

bp = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    # Por ahora solo tenemos un usuario
    if int(user_id) == 1:
        return User(id=1, email='admin@test.com', password='123', role='admin')
    return None

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
        email = form.email.data.strip() if form.email.data else ''
        password = form.password.data if form.password.data else ''
        
        # Validación manual en el servidor
        errors = {}
        if not email:
            errors['email'] = 'El email es requerido'
        elif '@' not in email or '.' not in email.split('@')[-1]:
            errors['email'] = 'Ingresa un email válido'
        
        if not password:
            errors['password'] = 'La contraseña es requerida'
        
        # Si no hay errores de validación, verificar credenciales
        if not errors:
            user = User.get(email)
            if user and user.check_password(password):
                login_user(user)
                flash('Inicio de sesión exitoso!', 'success')
                return redirect(url_for('main.home'))
            else:
                flash('Correo y/o contraseña inválidas', 'error')
        else:
            # Agregar errores al formulario para mostrar en el template
            if 'email' in errors:
                form.email.errors = [errors['email']]
            if 'password' in errors:
                form.password.errors = [errors['password']]
    
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('main.login'))

@bp.route('/home')
@login_required
def home():
    return render_template('home.html')