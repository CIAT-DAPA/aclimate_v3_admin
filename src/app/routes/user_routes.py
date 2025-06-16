from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.services.user_service import UserService
from app.services.role_service import RoleService
from app.forms.user_form import UserForm, UserEditForm
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

# Ruta: Eliminar usuario
@bp.route('/user/delete/<string:user_id>', methods=['POST'])
@token_required
def delete_user(user_id):
    """Eliminar usuario"""
    try:
        print(f"Intentando eliminar usuario con ID: {user_id}")
        
        success = user_service.delete(user_id)
        
        if success:
            flash('Usuario eliminado exitosamente.', 'success')
        else:
            flash('No se pudo eliminar el usuario.', 'danger')
            
    except ValueError as e:
        print(f"Error de validación: {e}")
        flash(f'Error: {str(e)}', 'danger')
    except Exception as e:
        print(f"Error inesperado eliminando usuario: {e}")
        flash(f'Error al eliminar usuario: {str(e)}', 'danger')
    return redirect(url_for('user.list_user'))

# Ruta: Editar usuario
@bp.route('/user/edit/<string:user_id>', methods=['GET', 'POST'])
@token_required
def edit_user(user_id):
    """Editar usuario - solo permite cambiar el rol"""
    try:
        # Obtener el usuario actual
        users = user_service.get_all()
        user = None
        for u in users:
            if u.get('id') == user_id:
                user = u
                break
        
        # Obtener todos los roles disponibles
        roles = role_service.get_all()
        
        # Crear formulario y llenar opciones de roles
        form = UserEditForm()
        form.role_id.choices = [(role['id'], role['display_name']) for role in roles]
        
        if request.method == 'GET':
            # Mostrar formulario con datos actuales
            form.role_id.data = user.get('role_id', '')
            return render_template('user/edit.html', form=form, user=user, roles=roles)
        
        elif request.method == 'POST' and form.validate_on_submit():
            # Procesar el cambio de rol
            try:
                print(f"Intentando cambiar rol del usuario {user_id} a {form.role_id.data}")
                
                # Verificar si el rol realmente cambió
                current_role_id = user.get('role_id', '')
                new_role_id = form.role_id.data
                
                if current_role_id == new_role_id:
                    flash('No se realizaron cambios - el usuario ya tiene ese rol asignado.', 'info')
                    return redirect(url_for('user.edit_user', user_id=user_id))
                
                # Asignar el nuevo rol
                success = user_service.assign_role(user_id, new_role_id)
                
                if success:
                    # Obtener el nombre del nuevo rol para el mensaje
                    new_role_name = next((role['display_name'] for role in roles if role['id'] == new_role_id), 'Desconocido')
                    flash(f'Rol actualizado exitosamente a "{new_role_name}".', 'success')
                    return redirect(url_for('user.list_user'))
                else:
                    flash('No se pudo actualizar el rol del usuario.', 'danger')
                    
            except ValueError as e:
                print(f"Error de validación: {e}")
                flash(f'Error: {str(e)}', 'danger')
            except Exception as e:
                print(f"Error inesperado actualizando rol: {e}")
                flash(f'Error al actualizar rol: {str(e)}', 'danger')
        
        else:
            # Errores de validación del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'Error en {field}: {error}', 'danger')
        
        # En caso de error, volver a mostrar el formulario
        return render_template('user/edit.html', form=form, user=user, roles=roles)
        
    except ValueError as e:
        print(f"Error obteniendo usuario: {e}")
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('user.list_user'))
    except Exception as e:
        print(f"Error inesperado en edit_user: {e}")
        flash(f'Error al cargar usuario: {str(e)}', 'danger')
        return redirect(url_for('user.list_user')) 