from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app.services.user_service import UserService
from app.services.role_service import RoleService
from app.forms.user_form import UserForm
from app.decorators import token_required

bp = Blueprint('user', __name__)
user_service = UserService()
role_service = RoleService()

# Ruta: Listar usuarios
@bp.route('/user', methods=['GET'])
@token_required
def list_user():
    form = UserForm()
    users = user_service.get_all()
    return render_template('user/list.html', users=users, form=form)

# Ruta: Solo crear usuario
@bp.route('/user/create', methods=['POST'])
@token_required
def create_user():
    form = UserForm()
    
    if form.validate_on_submit():
        try: 
            print(f"Intentando crear usuario: {form.username.data}")
            
            created_user = user_service.create(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                password=form.password.data
            )
            
            print(f"Usuario creado exitosamente: {created_user}")
            flash('Usuario agregado exitosamente.', 'success')
            
        except ValueError as e:
            print(f"Error de validación: {e}")
            flash(f'Error de validación: {str(e)}', 'danger')
        except Exception as e:
            print(f"Error inesperado: {e}")
            print(f"Tipo de error: {type(e)}")
            import traceback
            traceback.print_exc()
            flash(f'Error al agregar usuario: {str(e)}', 'danger')
    else:
        # Si hay errores de validación del formulario, mostrarlos
        print(f"Errores de formulario: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error en {field}: {error}', 'danger')
    
    # Siempre redirigir a la lista (formulario estará limpio)
    return redirect(url_for('user.list_user'))

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