from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.services.user_service import UserService
from app.services.role_service import RoleService
from app.forms.user_form import UserForm, UserEditForm
from app.decorators import token_required
from app.decorators.permissions import require_module_access
from app.config.permissions import Module, RolePermissionMapper

bp = Blueprint('user', __name__)
user_service = UserService()
role_service = RoleService()

# Ruta: Listar usuarios
@bp.route('/user', methods=['GET'])
@token_required
@require_module_access(Module.USER_MANAGEMENT)
def list_user():
    form = UserForm()
    users = user_service.get_all()
    from app.services.group_service import GroupService
    group_service = GroupService()
    countries = group_service.get_all()
    form.populate_countries(countries)
    return render_template('user/list.html', users=users, form=form, countries=countries)

# Ruta: Solo crear usuario
@bp.route('/user/create', methods=['POST'])
@token_required
@require_module_access(Module.USER_MANAGEMENT)
def create_user():
    # Obtener países disponibles para el formulario
    from app.services.group_service import GroupService
    group_service = GroupService()
    countries = group_service.get_all()
    
    form = UserForm()
    form.populate_countries(countries)
    
    if form.validate_on_submit():
        try: 
            print(f"Intentando crear usuario: {form.username.data}")
            
            # Crear el usuario básico primero
            created_user = user_service.create(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                password=form.password.data
            )
            
            print(f"Usuario creado exitosamente: {created_user}")
            
            # Si el usuario fue creado y se seleccionaron países, asignarlos
            if created_user and form.countries.data:
                try:
                    user_id = created_user.get('id')
                    selected_countries = form.countries.data
                    
                    print(f"Asignando países {selected_countries} al usuario {user_id}")
                    
                    # Usar el GroupService para asignar países
                    countries_assigned = group_service.assign_user_to_groups(user_id, selected_countries)
                    
                    if countries_assigned:
                        flash('Usuario creado y países asignados exitosamente.', 'success')
                    else:
                        flash('Usuario creado pero hubo problemas asignando países.', 'warning')
                        
                except Exception as e:
                    print(f"Error asignando países: {e}")
                    flash('Usuario creado pero no se pudieron asignar los países.', 'warning')
            else:
                flash('Usuario agregado exitosamente.', 'success')
            
        except ValueError as e:
            print(f"Error de validación: {e}")
            flash(f'Error de validación: {str(e)}', 'danger')
        except Exception as e:
            print(f"Error inesperado: {e}")
            print(f"Tipo de error: {type(e)}")
            import traceback
            traceback.print_exc()
            flash(f'Error creando usuario: {str(e)}', 'danger')
    else:
        # Si hay errores de validación
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error en {field}: {error}', 'danger')
    
    return redirect(url_for('user.list_user'))

# Ruta: Eliminar usuario
@bp.route('/user/delete/<string:user_id>', methods=['POST'])
@token_required
@require_module_access(Module.USER_MANAGEMENT)
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
@bp.route('/user/edit/<user_id>', methods=['GET', 'POST'])
@token_required
@require_module_access(Module.USER_MANAGEMENT)
def edit_user(user_id):
    """Editar usuario - permite cambiar nombre, apellido, email, rol y países"""
    try:
        # Obtener el usuario específico por ID
        user = user_service.get_by_id(user_id)
        
        # Obtener todos los roles disponibles
        roles = role_service.get_all()
        
        # Obtener todos los grupos/países disponibles
        from app.services.group_service import GroupService
        group_service = GroupService()
        countries = group_service.get_all()
        
        if not roles:
            flash('No se pudieron cargar los roles disponibles.', 'warning')
            return redirect(url_for('user.list_user'))
        
        if not countries:
            flash('No se pudieron cargar los países disponibles.', 'warning')
        
        # Crear formulario y llenar opciones
        form = UserEditForm()
        form.role_id.choices = [(role['id'], role['display_name']) for role in roles]
        form.countries.choices = [(country['name'], country['display_name']) for country in countries]
        
        if request.method == 'GET':
            # Mostrar formulario con datos actuales
            form.first_name.data = user.get('first_name', '')
            form.last_name.data = user.get('last_name', '')
            form.email.data = user.get('email', '')
            form.role_id.data = user.get('role_id', '')
            
            # Pre-seleccionar países del usuario - CORREGIR AQUÍ
            user_countries = user.get('countries', [])
            if user_countries and isinstance(user_countries, list):
                form.countries.data = [country['name'] for country in user_countries if isinstance(country, dict) and 'name' in country]
            else:
                form.countries.data = []  # Lista vacía si no hay países
            
            return render_template('user/edit.html', 
                                form=form, 
                                user=user, 
                                roles=roles, 
                                countries=countries)
        
        elif request.method == 'POST' and form.validate_on_submit():
            # Procesar la actualización del usuario
            try:
                print(f"Intentando actualizar usuario {user_id}")
                
                # Verificar qué campos han cambiado
                current_first_name = user.get('first_name', '')
                current_last_name = user.get('last_name', '')
                current_email = user.get('email', '')
                current_role_id = user.get('role_id', '')
                
                # CORREGIR AQUÍ - Manejar países actuales correctamente
                current_countries_data = user.get('countries', [])
                if current_countries_data and isinstance(current_countries_data, list):
                    current_countries = [country['name'] for country in current_countries_data if isinstance(country, dict) and 'name' in country]
                else:
                    current_countries = []
                
                new_first_name = form.first_name.data.strip() if form.first_name.data else ''
                new_last_name = form.last_name.data.strip() if form.last_name.data else ''
                new_email = form.email.data.strip() if form.email.data else ''
                new_role_id = form.role_id.data
                
                # CORREGIR AQUÍ - Manejar países nuevos correctamente
                new_countries = form.countries.data if form.countries.data else []
                
                # Flags para rastrear cambios
                user_data_changed = False
                role_changed = False
                countries_changed = False
                
                # Verificar cambios en datos básicos del usuario
                if (new_first_name != current_first_name or 
                    new_last_name != current_last_name or 
                    new_email != current_email):
                    user_data_changed = True
                
                # Verificar cambio de rol
                if new_role_id != current_role_id:
                    role_changed = True
                
                # Verificar cambio de países - CORREGIR AQUÍ
                if set(new_countries) != set(current_countries):
                    countries_changed = True
                    print(f"Países actuales: {current_countries}")
                    print(f"Países nuevos: {new_countries}")
                
                # Si no hay cambios
                if not user_data_changed and not role_changed and not countries_changed:
                    flash('No se realizaron cambios.', 'info')
                    return redirect(url_for('user.edit_user', user_id=user_id))
                
                # Lista para rastrear operaciones exitosas
                success_messages = []
                has_errors = False
                
                # Actualizar datos básicos del usuario si cambiaron
                if user_data_changed:
                    try:
                        # Determinar qué campos enviar (solo los que no están vacíos o han cambiado)
                        update_fields = {}
                        
                        if new_first_name or new_first_name != current_first_name:
                            update_fields['first_name'] = new_first_name if new_first_name else None
                        if new_last_name or new_last_name != current_last_name:
                            update_fields['last_name'] = new_last_name if new_last_name else None
                        if new_email or new_email != current_email:
                            update_fields['email'] = new_email if new_email else None
                        
                        if update_fields:
                            user_update_success = user_service.update(
                                user_id,
                                first_name=update_fields.get('first_name'),
                                last_name=update_fields.get('last_name'),
                                email=update_fields.get('email')
                            )
                            
                            if user_update_success:
                                success_messages.append('Información del usuario actualizada')
                            else:
                                flash('No se pudo actualizar la información del usuario.', 'danger')
                                has_errors = True
                        
                    except ValueError as e:
                        print(f"Error actualizando datos del usuario: {e}")
                        flash(f'Error actualizando información: {str(e)}', 'danger')
                        has_errors = True
                    except Exception as e:
                        print(f"Error inesperado actualizando datos del usuario: {e}")
                        flash(f'Error al actualizar información: {str(e)}', 'danger')
                        has_errors = True
                
                # Actualizar rol si cambió
                if role_changed:
                    try:
                        print(f"Cambiando rol de {current_role_id} a {new_role_id}")
                        
                        # Paso 1: Remover el rol actual si existe
                        if current_role_id:
                            try:
                                remove_success = user_service.remove_role(user_id, current_role_id)
                                if remove_success:
                                    print(f"Rol anterior {current_role_id} removido exitosamente")
                                else:
                                    print(f"No se pudo remover el rol anterior {current_role_id}")
                                    # Continuar con la asignación del nuevo rol aunque falle la remoción
                            except ValueError as e:
                                print(f"Error removiendo rol anterior: {e}")
                                # Si el error es que no tiene ese rol, continuar
                                if "no tiene asignado ese rol" in str(e).lower():
                                    print("El usuario no tenía ese rol asignado, continuando...")
                                else:
                                    # Si es otro error, mostrar advertencia pero continuar
                                    flash(f'Advertencia al remover rol anterior: {str(e)}', 'warning')
                            except Exception as e:
                                print(f"Error inesperado removiendo rol anterior: {e}")
                                flash(f'Advertencia al remover rol anterior: {str(e)}', 'warning')
                        
                        # Paso 2: Asignar el nuevo rol
                        role_update_success = user_service.assign_role(user_id, new_role_id)
                        
                        if role_update_success:
                            success_messages.append('Rol actualizado')
                        else:
                            flash('No se pudo actualizar el rol del usuario.', 'danger')
                            has_errors = True
                    
                    except ValueError as e:
                        print(f"Error actualizando rol: {e}")
                        flash(f'Error actualizando rol: {str(e)}', 'danger')
                        has_errors = True
                    except Exception as e:
                        print(f"Error inesperado actualizando rol: {e}")
                        flash(f'Error al actualizar rol: {str(e)}', 'danger')
                        has_errors = True
                
                # Actualizar países si cambiaron - usando GroupService
                if countries_changed:
                    try:
                        print(f"Cambiando países de {current_countries} a {new_countries}")
                        
                        # Usar el método del GroupService existente
                        countries_update_success = group_service.update_user_groups(user_id, new_countries)
                        
                        if countries_update_success:
                            success_messages.append('Países/grupos actualizados')
                        else:
                            flash('No se pudieron actualizar los países del usuario.', 'danger')
                            has_errors = True
                    
                    except Exception as e:
                        print(f"Error inesperado actualizando países: {e}")
                        flash(f'Error al actualizar países: {str(e)}', 'danger')
                        has_errors = True
                
                # Mostrar mensajes de éxito si los hay
                if success_messages and not has_errors:
                    message = 'Usuario actualizado exitosamente: ' + ', '.join(success_messages)
                    flash(message, 'success')
                    return redirect(url_for('user.list_user'))
                elif success_messages and has_errors:
                    message = 'Algunas actualizaciones fueron exitosas: ' + ', '.join(success_messages)
                    flash(message, 'warning')
                    return redirect(url_for('user.edit_user', user_id=user_id))
                else:
                    return redirect(url_for('user.edit_user', user_id=user_id))
                
            except Exception as e:
                print(f"Error general procesando actualizaciones: {e}")
                flash(f'Error procesando la actualización: {str(e)}', 'danger')
                return redirect(url_for('user.edit_user', user_id=user_id))
        
        else:
            # Errores de validación del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'Error en {field}: {error}', 'danger')
            
            return render_template('user/edit.html', 
                                form=form, 
                                user=user, 
                                roles=roles, 
                                countries=countries)
        
    except ValueError as e:
        print(f"Error obteniendo usuario: {e}")
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('user.list_user'))
    except Exception as e:
        print(f"Error inesperado en edit_user: {e}")
        flash('Error cargando la página de edición.', 'danger')
        return redirect(url_for('user.list_user'))
    
@bp.route('/users/bulk_action', methods=['POST'])
@token_required
@require_module_access(Module.USER_MANAGEMENT)
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    if not ids:
        flash('No se seleccionaron usuarios.', 'warning')
        return redirect(url_for('user.list_user'))

    count = 0
    for loc_id in ids:
        try:
            if action == 'disable':
                if user_service.delete(loc_id):
                    count += 1
        except Exception:
            continue

    if action == 'disable':
        flash(f'{count} usuarios deshabilitado(s).', 'warning')
    else:
        flash('Acción no reconocida.', 'danger')
    return redirect(url_for('user.list_user'))