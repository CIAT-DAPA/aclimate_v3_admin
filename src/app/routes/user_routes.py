from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from flask_babel import _
from app.services.user_service import UserService
from app.services.role_service import RoleService
from app.forms.user_form import UserForm
from app.decorators import token_required

bp = Blueprint('user', __name__)
user_service = UserService()
role_service = RoleService()

# Ruta: Lista de usuarios
@bp.route('/user', methods=['GET', 'POST'])
@token_required
def list_user():
    form = UserForm()
    
    # Cargar roles disponibles para el formulario
    roles = role_service.get_active_roles()
    form.role_id.choices = [(role['id'], role['name']) for role in roles]
    
    if form.validate_on_submit():
        try:
            # Obtener el nombre del rol seleccionado
            selected_role = role_service.get_by_id(form.role_id.data)
            role_name = selected_role['name'] if selected_role else 'Unknown'
            
            user_service.create(
                username=form.username.data,
                email=form.email.data,
                role_id=form.role_id.data,
                role_name=role_name
            )
            flash(_('Usuario agregado exitosamente.'), 'success')
            return redirect(url_for('user.list_user'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(_(f'Error al agregar usuario: {str(e)}'), 'danger')

    users = user_service.get_all()
    return render_template('user/list.html', users=users, form=form)

# Ruta: Agregar usuario
@bp.route('/user/add', methods=['GET', 'POST'])
@token_required
def add_user():
    form = UserForm()
    
    # Cargar roles disponibles para el formulario
    roles = role_service.get_active_roles()
    form.role_id.choices = [(role['id'], role['name']) for role in roles]
    
    if form.validate_on_submit():
        try:
            # Obtener el nombre del rol seleccionado
            selected_role = role_service.get_by_id(form.role_id.data)
            role_name = selected_role['name'] if selected_role else 'Unknown'
            
            user_service.create(
                username=form.username.data,
                email=form.email.data,
                role_id=form.role_id.data,
                role_name=role_name
            )
            flash(_('Usuario agregado exitosamente.'), 'success')
            return redirect(url_for('user.list_user'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(_(f'Error al agregar usuario: {str(e)}'), 'danger')

    return render_template('user/add.html', form=form)

# Ruta: Ver detalle del usuario
@bp.route('/user/view/<int:id>')
@token_required
def view_user(id):
    user = user_service.get_by_id(id)
    if not user:
        flash(_('Usuario no encontrado.'), 'danger')
        return redirect(url_for('user.list_user'))
    
    return render_template('user/view.html', user=user)

# Ruta: Editar usuario
@bp.route('/user/edit/<int:id>', methods=['GET', 'POST'])
@token_required
def edit_user(id):
    existing = user_service.get_by_id(id)
    if not existing:
        flash(_('Usuario no encontrado.'), 'danger')
        return redirect(url_for('user.list_user'))

    form = UserForm()
    
    # Cargar roles disponibles para el formulario
    roles = role_service.get_active_roles()
    form.role_id.choices = [(role['id'], role['name']) for role in roles]
    
    # Prellenar formulario con datos existentes en GET
    if request.method == 'GET':
        form.username.data = existing['username']
        form.email.data = existing['email']
        form.role_id.data = existing['role_id']

    if form.validate_on_submit():
        try:
            # Obtener el nombre del rol seleccionado
            selected_role = role_service.get_by_id(form.role_id.data)
            role_name = selected_role['name'] if selected_role else 'Unknown'
            
            user_service.update(
                user_id=id,
                username=form.username.data,
                email=form.email.data,
                role_id=form.role_id.data,
                role_name=role_name
            )
            flash(_('Usuario actualizado correctamente.'), 'success')
            return redirect(url_for('user.list_user'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(_(f'Error al actualizar usuario: {str(e)}'), 'danger')

    return render_template('user/edit.html', form=form, user=existing)

# Ruta: Eliminar (deshabilitar) usuario
@bp.route('/user/delete/<int:id>')
@token_required
def delete_user(id):
    existing = user_service.get_by_id(id)
    if not existing:
        flash(_('Usuario no encontrado.'), 'danger')
        return redirect(url_for('user.list_user'))
    
    # Verificar si es un usuario crítico que no se puede deshabilitar
    if existing['username'].lower() in ['admin', 'administrator']:
        flash(_('No se puede deshabilitar el usuario administrador.'), 'danger')
        return redirect(url_for('user.list_user'))

    if not user_service.delete(id):
        flash(_('No se pudo deshabilitar el usuario.'), 'danger')
    else:
        flash(_('Usuario deshabilitado.'), 'warning')

    return redirect(url_for('user.list_user'))

# Ruta: Recuperar usuario
@bp.route('/user/reset/<int:id>')
@token_required
def reset_user(id):
    existing = user_service.get_by_id(id)
    if not existing:
        flash(_('Usuario no encontrado.'), 'danger')
        return redirect(url_for('user.list_user'))

    if user_service.restore(id):
        flash(_('Usuario recuperado.'), 'success')
    else:
        flash(_('No se pudo recuperar el usuario.'), 'danger')

    return redirect(url_for('user.list_user'))

# Ruta: API para buscar usuarios
@bp.route('/user/search')
@token_required
def search_users():
    query = request.args.get('q', '').strip()
    if query:
        users = user_service.search_users(query)
    else:
        users = user_service.get_active_users()
    
    return jsonify({
        'users': users,
        'count': len(users)
    })

# Ruta: API para obtener usuarios por rol
@bp.route('/user/by-role/<int:role_id>')
@token_required
def get_users_by_role(role_id):
    users = user_service.get_users_by_role(role_id)
    return jsonify({
        'users': users,
        'count': len(users),
        'role_id': role_id
    })

# Ruta: Obtener estadísticas de usuarios
@bp.route('/user/stats')
@token_required
def get_user_stats():
    stats = user_service.get_user_count()
    return jsonify(stats)