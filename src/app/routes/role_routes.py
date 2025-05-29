from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app.services.role_service import RoleService
from app.forms.role_form import RoleForm

bp = Blueprint('role', __name__)
role_service = RoleService()

# Ruta: Lista de roles
@bp.route('/role', methods=['GET', 'POST'])
@login_required
def list_role():
    form = RoleForm()
    if form.validate_on_submit():
        try:
            # Convertir módulos seleccionados a diccionario
            modules = {}
            available_modules = role_service.get_available_modules()
            
            for module in available_modules:
                modules[module] = module in form.modules.data
            
            new_role_data = {
                'name': form.name.data,
                'description': form.description.data,
                'modules': modules,
                'enable': form.enable.data
            }
            role_service.create(new_role_data)
            flash('Rol agregado exitosamente.', 'success')
            return redirect(url_for('role.list_role'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error al agregar rol: {str(e)}', 'error')

    roles = role_service.get_all()
    return render_template('role/list.html', roles=roles, form=form)

# Ruta: Agregar rol
@bp.route('/role/add', methods=['GET', 'POST'])
@login_required
def add_role():
    form = RoleForm()
    if form.validate_on_submit():
        try:
            # Convertir módulos seleccionados a diccionario
            modules = {}
            available_modules = role_service.get_available_modules()
            
            for module in available_modules:
                modules[module] = module in form.modules.data
            
            role_data = {
                'name': form.name.data,
                'description': form.description.data,
                'modules': modules,
                'enable': form.enable.data
            }
            role_service.create(role_data)
            flash('Rol agregado exitosamente.', 'success')
            return redirect(url_for('role.list_role'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error al agregar rol: {str(e)}', 'error')
    
    return render_template('role/add.html', form=form)

# Ruta: Editar rol
@bp.route('/role/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_role(id):
    existing = role_service.get_by_id(id)
    if not existing:
        flash('Rol no encontrado.', 'error')
        return redirect(url_for('role.list_role'))

    # Crear formulario con datos existentes
    form = RoleForm()
    
    if request.method == 'GET':
        # Prellenar formulario con datos existentes
        form.name.data = existing['name']
        form.description.data = existing['description']
        form.enable.data = existing.get('enable', True)
        
        # Prellenar módulos activos
        active_modules = []
        for module, access in existing.get('modules', {}).items():
            if access:
                active_modules.append(module)
        form.modules.data = active_modules

    if form.validate_on_submit():
        try:
            # Convertir módulos seleccionados a diccionario
            modules = {}
            available_modules = role_service.get_available_modules()
            
            for module in available_modules:
                modules[module] = module in form.modules.data
            
            update_data = {
                'name': form.name.data,
                'description': form.description.data,
                'modules': modules,
                'enable': form.enable.data
            }
            
            role_service.update(id, update_data)
            flash('Rol actualizado correctamente.', 'success')
            return redirect(url_for('role.list_role'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error al actualizar rol: {str(e)}', 'error')

    return render_template('role/edit.html', form=form, role=existing)

# Ruta: Eliminar (deshabilitar) rol
@bp.route('/role/delete/<int:id>')
@login_required
def delete_role(id):
    existing = role_service.get_by_id(id)
    if not existing:
        flash('Rol no encontrado.', 'error')
        return redirect(url_for('role.list_role'))
    
    # Verificar si es un rol crítico que no se puede deshabilitar
    if existing['name'].lower() in ['admin', 'administrador']:
        flash('No se puede deshabilitar el rol de administrador.', 'error')
        return redirect(url_for('role.list_role'))
    
    if not role_service.delete(id):
        flash('No se pudo deshabilitar el rol.', 'error')
    else:
        flash('Rol deshabilitado.', 'warning')
    
    return redirect(url_for('role.list_role'))

# Ruta: Recuperar rol
@bp.route('/role/restore/<int:id>')
@login_required
def restore_role(id):
    existing = role_service.get_by_id(id)
    if not existing:
        flash('Rol no encontrado.', 'error')
        return redirect(url_for('role.list_role'))

    if role_service.restore(id):
        flash('Rol recuperado exitosamente.', 'success')
    else:
        flash('No se pudo recuperar el rol.', 'error')
    
    return redirect(url_for('role.list_role'))

# Ruta: Ver detalle del rol
@bp.route('/role/view/<int:id>')
@login_required
def view_role(id):
    role = role_service.get_by_id(id)
    if not role:
        flash('Rol no encontrado.', 'error')
        return redirect(url_for('role.list_role'))
    
    return render_template('role/view.html', role=role)

# Ruta: API para obtener módulos disponibles (para formularios dinámicos)
@bp.route('/role/modules')
@login_required
def get_modules():
    modules = role_service.get_available_modules()
    return jsonify(modules)

# Ruta: API para verificar acceso a módulo
@bp.route('/role/<int:role_id>/module/<module_name>/access')
@login_required
def check_module_access(role_id, module_name):
    has_access = role_service.has_module_access(role_id, module_name)
    return jsonify({'has_access': has_access})

# Ruta: Actualizar acceso a módulo específico (AJAX)
@bp.route('/role/<int:role_id>/module/<module_name>/toggle', methods=['POST'])
@login_required
def toggle_module_access(role_id, module_name):
    try:
        current_access = role_service.has_module_access(role_id, module_name)
        new_access = not current_access
        
        updated_role = role_service.update_module_access(role_id, module_name, new_access)
        if updated_role:
            return jsonify({
                'success': True,
                'new_access': new_access,
                'message': f'Acceso al módulo {module_name} {"habilitado" if new_access else "deshabilitado"}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Rol no encontrado'
            }), 404
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500