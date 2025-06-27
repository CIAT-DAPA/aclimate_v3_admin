from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app.forms.role_form import RoleForm, RoleEditForm
from app.services.role_service import RoleService
from app.decorators import token_required
from app.decorators.permissions import require_module_access
from app.config.permissions import Module, RolePermissionMapper

bp = Blueprint('role', __name__)
role_service = RoleService()

# Ruta: Lista de roles
@bp.route('/role', methods=['GET'])
@token_required
@require_module_access(Module.USER_MANAGEMENT)
def list_role():
    form = RoleForm()
    roles = role_service.get_all()

    # Agregar información de sincronización
    sync_info = role_service.sync_role_modules()
    
    return render_template('role/list.html', 
                         roles=roles, 
                         form=form,
                         sync_info=sync_info.get('sync_result', {}))

# Ruta: Crear roles con módulos
@bp.route('/role/create', methods=['POST'])
@token_required
@require_module_access(Module.USER_MANAGEMENT)
def create_role():
    form = RoleForm()
    
    if form.validate_on_submit():
        try: 
            print(f"Intentando crear rol: {form.name.data}")
            print(f"Módulos seleccionados: {form.modules.data}")

            result = role_service.create(
                name=form.name.data,
                description=form.description.data,
                modules=form.modules.data
            )

            if result.get('success'):
                print(f"Rol creado exitosamente: {result}")
                flash('Rol agregado exitosamente con acceso a los módulos seleccionados.', 'success')
            else:
                flash(f'Error al crear rol: {result.get("error", "Error desconocido")}', 'danger')

        except ValueError as e:
            print(f"Error de validación: {e}")
            flash(f'Error de validación: {str(e)}', 'danger')
        except Exception as e:
            print(f"Error inesperado: {e}")
            import traceback
            traceback.print_exc()
            flash(f'Error al agregar rol: {str(e)}', 'danger')
    else:
        # Si hay errores de validación del formulario, mostrarlos
        print(f"Errores de formulario: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error en {field}: {error}', 'danger')
    
    return redirect(url_for('role.list_role'))

# Ruta: Editar módulos de un rol
@bp.route('/role/<role_name>/edit_modules', methods=['GET', 'POST'])
@token_required
@require_module_access(Module.USER_MANAGEMENT)
def edit_role_modules(role_name):
    role_info = role_service.get_role_with_modules(role_name)
    
    if not role_info:
        flash('Rol no encontrado.', 'error')
        return redirect(url_for('role.list_role'))
    
    form = RoleEditForm()
    
    if request.method == 'GET':
        # Prellenar formulario con datos existentes
        form.name.data = role_info['name']
        form.description.data = role_info['description']
        form.modules.data = [module.value for module in role_info['modules']]
    
    if form.validate_on_submit():
        try:
            # Solo actualizar módulos localmente (no cambiar nombre/descripción en Keycloak)
            success = role_service.update_local_modules(role_name, form.modules.data)
            
            if success:
                flash(f'Módulos del rol "{role_name}" actualizados exitosamente.', 'success')
                return redirect(url_for('role.list_role'))
            else:
                flash('Error al actualizar módulos del rol.', 'danger')
                
        except Exception as e:
            print(f"Error al actualizar módulos: {e}")
            flash(f'Error al actualizar rol: {str(e)}', 'danger')
    
    return render_template('role/edit_modules.html', form=form, role=role_info)

# Ruta: Eliminar rol
@bp.route('/role/<role_id>/delete', methods=['POST'])
@token_required
@require_module_access(Module.USER_MANAGEMENT)
def delete_role(role_id):
    try:
        # Obtener nombre del rol antes de eliminarlo
        role_name = request.form.get('role_name')
        
        print(f"Intentando eliminar rol ID: {role_id}, Nombre: {role_name}")
        
        success = role_service.delete(role_id, role_name)
        
        if success:
            flash('Rol eliminado exitosamente de Keycloak y configuración local.', 'success')
        else:
            flash('Error al eliminar el rol.', 'danger')
            
    except Exception as e:
        print(f"Error eliminando rol: {e}")
        flash(f'Error al eliminar rol: {str(e)}', 'danger')
    
    return redirect(url_for('role.list_role'))

@bp.route('/role/bulk_action', methods=['POST'])
@token_required
@require_module_access(Module.USER_MANAGEMENT)
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    if not ids:
        flash('No se seleccionaron roles.', 'warning')
        return redirect(url_for('role.list_role'))

    count = 0
    for loc_id in ids:
        try:
            if action == 'disable':
                if role_service.delete(loc_id):
                    count += 1
        except Exception:
            continue

    if action == 'disable':
        flash(f'{count} roles deshabilitados.', 'warning')
    else:
        flash('Acción no reconocida.', 'danger')
    return redirect(url_for('role.list_role'))