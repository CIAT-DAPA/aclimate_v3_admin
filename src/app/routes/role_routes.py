from flask import Blueprint, render_template, redirect, url_for, flash
from app.forms.role_form import RoleForm
from app.services.role_service import RoleService
from app.decorators import token_required

bp = Blueprint('role', __name__)
role_service = RoleService()

# Ruta: Lista de roles
@bp.route('/role', methods=['GET'])
@token_required
def list_role():
    form = RoleForm()
    roles = role_service.get_all()
    return render_template('role/list.html', roles=roles, form=form)

# Ruta: Solo crear roles
@bp.route('/role/create', methods=['POST'])
@token_required
def create_role():
    form = RoleForm()
    
    if form.validate_on_submit():
        try: 
            print(f"Intentando crear rol: {form.name.data}")

            created_role = role_service.create(
                name=form.name.data,
                description=form.description.data
            )

            print(f"Rol creado exitosamente: {created_role}")
            flash('Rol agregado exitosamente.', 'success')

        except ValueError as e:
            print(f"Error de validación: {e}")
            flash(f'Error de validación: {str(e)}', 'danger')
        except Exception as e:
            print(f"Error inesperado: {e}")
            print(f"Tipo de error: {type(e)}")
            import traceback
            traceback.print_exc()
            flash(f'Error al agregar rol: {str(e)}', 'danger')
    else:
        # Si hay errores de validación del formulario, mostrarlos
        print(f"Errores de formulario: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error en {field}: {error}', 'danger')
    
    # Siempre redirigir a la lista (formulario estará limpio)
    return redirect(url_for('role.list_role'))

# Ruta: Eliminar rol
@bp.route('/role/delete/<string:role_id>', methods=['POST'])
@token_required
def delete_role(role_id):
    """Eliminar rol"""
    try:
        print(f"Intentando eliminar rol con ID: {role_id}")
        
        success = role_service.delete(role_id)
        
        if success:
            flash('Rol eliminado exitosamente.', 'success')
        else:
            flash('No se pudo eliminar el rol.', 'danger')
            
    except ValueError as e:
        print(f"Error de validación: {e}")
        flash(f'Error: {str(e)}', 'danger')
    except Exception as e:
        print(f"Error inesperado eliminando rol: {e}")
        flash(f'Error al eliminar rol: {str(e)}', 'danger')
    return redirect(url_for('role.list_role'))