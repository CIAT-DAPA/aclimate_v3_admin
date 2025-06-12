from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
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
            flash('Usuario agregado exitosamente.', 'success')
            return redirect(url_for('user.list_user'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Error al agregar usuario: {str(e)}', 'danger')

    users = user_service.get_all()
    return render_template('user/list.html', users=users, form=form)

@bp.route('/user/assign-role/<int:user_id>', methods=['POST'])
@token_required
def assign_role(user_id):
    """Asignar rol a usuario usando el nuevo método del servicio"""
    try:
        data = request.get_json()
        role_id = data.get('role_id')
        
        if not role_id:
            return jsonify({'success': False, 'message': 'Role ID requerido'}), 400
        
        success = user_service.assign_role(user_id, role_id)
        
        if success:
            # Obtener información del rol para la respuesta
            role = role_service.get_by_id(role_id)
            return jsonify({
                'success': True,
                'message': f'Rol asignado correctamente',
                'role_name': role['name'] if role else 'Unknown'
            })
        else:
            return jsonify({'success': False, 'message': 'Error asignando rol'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500