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
    if form.validate_on_submit():
        user = User.get(form.email.data)
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Inicio de sesión exitoso!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Email o contraseña incorrectos', 'danger')
    
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
