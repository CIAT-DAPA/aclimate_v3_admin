from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app.services.user_service import UserService
from app.services.role_service import RoleService
from app.forms.user_form import UserForm, UserEditForm
from app.decorators import token_required
from app.decorators.permissions import require_module_access
from app.config.permissions import Module
from aclimate_v3_orm.services import MngCountryService
from aclimate_v3_orm.services.user_access_service import UserAccessService
from aclimate_v3_orm.schemas import UserAccessCreate
from aclimate_v3_orm.enums import Modules

bp = Blueprint('user', __name__)
user_service = UserService()
role_service = RoleService()
country_service = MngCountryService()
user_access_service = UserAccessService()

# Ruta: Listar usuarios
@bp.route('/user', methods=['GET'])
@token_required
@require_module_access(Module.USER_MANAGEMENT, permission_type='read')
def list_user():
    # Check create permission for showing add button
    can_create = current_user.has_module_access(Module.USER_MANAGEMENT.value, 'create')
    
    form = UserForm()
    users = user_service.get_all()
    
    # Obtener países desde el servicio del ORM
    countries_objs = country_service.get_all_enable(enabled=True)
    # Convertir a diccionarios para compatibilidad con el template
    countries = [
        {
            'id': c.id,
            'name': c.name,
            'display_name': c.name,
            'iso_alpha_2': c.iso2  # El schema usa 'iso2', no 'iso_alpha_2'
        } 
        for c in countries_objs
    ]
    
    # Obtener roles disponibles
    roles = role_service.get_all()
    
    form.populate_roles(roles)
    return render_template('user/list.html', users=users, form=form, can_create=can_create)

# Ruta: Solo crear usuario
@bp.route('/user/create', methods=['POST'])
@token_required
@require_module_access(Module.USER_MANAGEMENT, permission_type='create')
def create_user():
    """Crear usuario en Keycloak y en la base de datos local"""
    # Obtener roles disponibles
    roles = role_service.get_all()
    
    form = UserForm()
    form.populate_roles(roles)
    
    if form.validate_on_submit():
        try: 
            print(f"Creando usuario completo (Keycloak + BD): {form.username.data}")
            
            # Crear usuario en Keycloak y BD local usando el método integrado
            created_user = user_service.create_complete_user(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                role_id=form.role_id.data,
                enabled=True
            )
            
            if not created_user:
                flash('Error creando usuario en Keycloak o base de datos.', 'danger')
                return redirect(url_for('user.list_user'))
            
            print(f"Usuario creado exitosamente - Keycloak ID: {created_user['keycloak_id']}, DB ID: {created_user['db_id']}")
            
            # Mensaje de éxito
            flash(
                f"Usuario '{form.username.data}' creado exitosamente. "
                f"Usa el botón '🛡️ Gestionar permisos' para asignar módulos y permisos CRUD.", 
                'success'
            )
            
        except ValueError as e:
            print(f"Error de validación: {e}")
            flash(f'Error de validación: {str(e)}', 'danger')
        except Exception as e:
            print(f"Error inesperado: {e}")
            import traceback
            traceback.print_exc()
            flash(f'Error creando usuario: {str(e)}', 'danger')
    else:
        # Si hay errores de validación del formulario
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error en {field}: {error}', 'danger')
    
    return redirect(url_for('user.list_user'))

# Ruta: Eliminar usuario
@bp.route('/user/delete/<int:user_id>', methods=['POST'])
@token_required
@require_module_access(Module.USER_MANAGEMENT, permission_type='delete')
def delete_user(user_id):
    """Eliminar usuario de Keycloak y deshabilitar en base de datos"""
    try:
        print(f"Eliminando usuario con ID de BD: {user_id}")
        
        # Obtener información del usuario para conseguir el keycloak_id
        user = user_service.get_by_id(user_id)
        
        if not user:
            flash('Usuario no encontrado.', 'danger')
            return redirect(url_for('user.list_user'))
        
        keycloak_id = user.get('keycloak_id')
        
        if not keycloak_id:
            flash('El usuario no tiene un ID de Keycloak asociado.', 'warning')
            # Intentar solo eliminar de BD local
            success = user_service.delete(user_id)
            if success:
                flash('Usuario deshabilitado en base de datos local.', 'success')
            else:
                flash('No se pudo deshabilitar el usuario.', 'danger')
            return redirect(url_for('user.list_user'))
        
        # Eliminar de Keycloak y deshabilitar en BD
        success = user_service.delete_complete_user(
            db_user_id=user_id,
            keycloak_user_id=keycloak_id
        )
        
        if success:
            flash('Usuario eliminado de Keycloak y deshabilitado en base de datos.', 'success')
        else:
            flash('Hubo problemas al eliminar el usuario.', 'danger')
            
    except ValueError as e:
        print(f"Error de validación: {e}")
        flash(f'Error: {str(e)}', 'danger')
    except Exception as e:
        print(f"Error inesperado eliminando usuario: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error al eliminar usuario: {str(e)}', 'danger')
    
    return redirect(url_for('user.list_user'))

# Ruta: Editar usuario
@bp.route('/user/edit/<user_id>', methods=['GET', 'POST'])
@token_required
@require_module_access(Module.USER_MANAGEMENT, permission_type='update')
def edit_user(user_id):
    """Editar usuario - permite cambiar nombre, apellido, email, rol y países"""
    try:
        # Obtener el usuario específico por ID
        user = user_service.get_by_id(user_id)
        
        # Obtener todos los roles disponibles
        roles = role_service.get_all()
        
        # Obtener todos los países disponibles desde el ORM
        countries_objs = country_service.get_all_enable(enabled=True)
        countries = [
            {
                'id': c.id,
                'name': c.name,
                'display_name': c.name,
                'iso_alpha_2': c.iso2  # El schema usa 'iso2', no 'iso_alpha_2'
            } 
            for c in countries_objs
        ]
        
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
                print(f"Actualizando usuario {user_id} en Keycloak y BD")
                
                # Obtener keycloak_id del usuario
                keycloak_id = user.get('keycloak_id')
                
                if not keycloak_id:
                    flash('El usuario no tiene un ID de Keycloak asociado. No se puede actualizar.', 'danger')
                    return redirect(url_for('user.edit_user', user_id=user_id))
                
                # Obtener valores del formulario
                new_first_name = form.first_name.data.strip() if form.first_name.data else None
                new_last_name = form.last_name.data.strip() if form.last_name.data else None
                new_email = form.email.data.strip() if form.email.data else None
                new_role_id = form.role_id.data
                new_countries = form.countries.data if form.countries.data else []
                
                # Obtener valores actuales
                current_first_name = user.get('first_name', '')
                current_last_name = user.get('last_name', '')
                current_email = user.get('email', '')
                current_role_id = user.get('role_id')
                current_countries_data = user.get('countries', [])
                current_countries = [country['name'] for country in current_countries_data if isinstance(country, dict) and 'name' in country]
                
                # Determinar qué cambió
                first_name_changed = new_first_name != current_first_name
                last_name_changed = new_last_name != current_last_name
                email_changed = new_email != current_email
                role_changed = new_role_id != current_role_id
                countries_changed = set(new_countries) != set(current_countries)
                
                # Verificar si hay cambios
                if not (first_name_changed or last_name_changed or email_changed or role_changed or countries_changed):
                    flash('No se realizaron cambios.', 'info')
                    return redirect(url_for('user.edit_user', user_id=user_id))
                
                print(f"Cambios detectados - Nombre: {first_name_changed}, Apellido: {last_name_changed}, Email: {email_changed}, Rol: {role_changed}, Países: {countries_changed}")
                
                success_messages = []
                has_errors = False
                
                # Actualizar usuario en Keycloak y BD (datos personales y rol)
                if first_name_changed or last_name_changed or email_changed or role_changed:
                    update_success = user_service.update_complete_user(
                        db_user_id=int(user_id),
                        keycloak_user_id=keycloak_id,
                        first_name=new_first_name if first_name_changed else None,
                        last_name=new_last_name if last_name_changed else None,
                        email=new_email if email_changed else None,
                        role_id=new_role_id if role_changed else None
                    )
                    
                    if update_success:
                        if first_name_changed or last_name_changed or email_changed:
                            success_messages.append('Información personal actualizada en Keycloak')
                        if role_changed:
                            success_messages.append('Rol actualizado en base de datos')
                    else:
                        flash('Error actualizando usuario en Keycloak o base de datos.', 'danger')
                        has_errors = True
                
                # Actualizar países si cambiaron
                if countries_changed and not has_errors:
                    try:
                        print(f"Actualizando países: {current_countries} → {new_countries}")
                        
                        # Obtener IDs de países
                        country_id_map = {c.name: c.id for c in countries_objs}
                        
                        # Eliminar accesos de países que ya no están seleccionados
                        countries_to_remove = set(current_countries) - set(new_countries)
                        deleted_total = 0
                        for country_name in countries_to_remove:
                            if country_name in country_id_map:
                                country_id = country_id_map[country_name]
                                # Eliminar todos los accesos de este usuario-país
                                deleted_count = user_access_service.delete_by_user_and_country(
                                    user_id=int(user_id),
                                    country_id=country_id
                                )
                                deleted_total += deleted_count
                                print(f"  🗑️  Eliminados {deleted_count} accesos de {country_name}")
                        
                        if deleted_total > 0:
                            print(f"Total de accesos eliminados: {deleted_total}")
                        
                        # Crear accesos para nuevos países
                        countries_to_add = set(new_countries) - set(current_countries)
                        modules_to_assign = [
                            Modules.GEOGRAPHIC,
                            Modules.CLIMATE_DATA,
                            Modules.CROP_DATA,
                            Modules.INDICATORS_DATA,
                            Modules.STRESS_DATA,
                            Modules.PHENOLOGICAL_STAGE,
                        ]
                        
                        created_count = 0
                        for country_name in countries_to_add:
                            if country_name not in country_id_map:
                                continue
                                
                            country_id = country_id_map[country_name]
                            
                            for module in modules_to_assign:
                                try:
                                    access_data = UserAccessCreate(
                                        user_id=int(user_id),
                                        country_id=country_id,
                                        role_id=new_role_id,
                                        module=module,
                                        create=False,
                                        read=True,
                                        update=False,
                                        delete=False
                                    )
                                    user_access_service.create(access_data)
                                    created_count += 1
                                except Exception as e:
                                    if 'duplicate' not in str(e).lower() and 'unique' not in str(e).lower():
                                        print(f"Error creando acceso: {e}")
                        
                        # Construir mensaje informativo
                        if created_count > 0 or deleted_total > 0:
                            parts = []
                            if created_count > 0:
                                parts.append(f'{created_count} accesos creados')
                            if deleted_total > 0:
                                parts.append(f'{deleted_total} accesos eliminados')
                            success_messages.append(f'Países actualizados ({", ".join(parts)})')
                        else:
                            success_messages.append('Países actualizados')
                            
                    except Exception as e:
                        print(f"Error actualizando países: {e}")
                        import traceback
                        traceback.print_exc()
                        flash(f'Error al actualizar países: {str(e)}', 'warning')
                        has_errors = True
                
                # Mostrar mensajes finales
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
                import traceback
                traceback.print_exc()
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
@require_module_access(Module.USER_MANAGEMENT, permission_type='delete')
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

# Ruta: Gestionar permisos de usuario
@bp.route('/user/<int:user_id>/permissions', methods=['GET', 'POST'])
@token_required
@require_module_access(Module.USER_MANAGEMENT, permission_type='update')
def manage_permissions(user_id):
    """Gestionar permisos de usuario por país y módulo"""
    try:
        # Obtener información del usuario
        user = user_service.get_by_id(user_id)
        if not user:
            flash('Usuario no encontrado.', 'danger')
            return redirect(url_for('user.list_user'))
        
        # Obtener todos los países disponibles
        countries_objs = country_service.get_all_enable(enabled=True)
        countries = [
            {
                'id': c.id,
                'name': c.name,
                'display_name': c.name,
            } 
            for c in countries_objs
        ]
        
        # Obtener permisos actuales del usuario
        user_accesses = user_access_service.get_by_user_id(user_id)
        
        # Organizar permisos por país y módulo
        permissions_by_country = {}
        for access in user_accesses:
            country_id = access.country_id
            if country_id not in permissions_by_country:
                permissions_by_country[country_id] = {}
            
            permissions_by_country[country_id][access.module.value] = {
                'create': access.create,
                'read': access.read,
                'update': access.update,
                'delete': access.delete,
            }
        
        # Módulos disponibles
        available_modules = [
            {'value': 'geographic', 'name': 'Módulo Geográfico', 'icon': 'fa-globe'},
            {'value': 'climate_data', 'name': 'Datos Climáticos', 'icon': 'fa-cloud-sun'},
            {'value': 'crop_data', 'name': 'Datos de Cultivos', 'icon': 'fa-seedling'},
            {'value': 'stress_data', 'name': 'Datos de Estrés', 'icon': 'fa-exclamation-triangle'},
            {'value': 'phenological_stage', 'name': 'Etapas Fenológicas', 'icon': 'fa-calendar-alt'},
            {'value': 'indicators_data', 'name': 'Indicadores', 'icon': 'fa-chart-line'},
            {'value': 'user_management', 'name': 'Gestión de Usuarios', 'icon': 'fa-users'},
            {'value': 'configuration', 'name': 'Configuración', 'icon': 'fa-cog'},
        ]
        
        if request.method == 'POST':
            try:
                # Procesar los permisos enviados desde el formulario
                # El formulario envía: country_{country_id}_module_{module_value}_permission
                
                # Primero, eliminar todos los permisos existentes del usuario
                # (luego crearemos los nuevos)
                for country in countries:
                    user_access_service.delete_by_user_and_country(user_id, country['id'])
                
                # Crear nuevos permisos según el formulario
                created_count = 0
                for country in countries:
                    country_id = country['id']
                    
                    for module in available_modules:
                        module_value = module['value']
                        
                        # Verificar si este módulo está seleccionado para este país
                        checkbox_name = f"country_{country_id}_module_{module_value}"
                        if checkbox_name in request.form:
                            # Obtener permisos CRUD
                            create_perm = f"country_{country_id}_module_{module_value}_create" in request.form
                            read_perm = f"country_{country_id}_module_{module_value}_read" in request.form
                            update_perm = f"country_{country_id}_module_{module_value}_update" in request.form
                            delete_perm = f"country_{country_id}_module_{module_value}_delete" in request.form
                            
                            # Crear el acceso
                            try:
                                module_enum = Modules(module_value)
                                access_data = UserAccessCreate(
                                    user_id=user_id,
                                    country_id=country_id,
                                    role_id=user['role_id'],
                                    module=module_enum,
                                    create=create_perm,
                                    read=read_perm,
                                    update=update_perm,
                                    delete=delete_perm
                                )
                                user_access_service.create(access_data)
                                created_count += 1
                            except Exception as e:
                                print(f"Error creando permiso: {e}")
                
                flash(f'Permisos actualizados exitosamente. {created_count} permisos configurados.', 'success')
                return redirect(url_for('user.manage_permissions', user_id=user_id))
                
            except Exception as e:
                print(f"Error actualizando permisos: {e}")
                import traceback
                traceback.print_exc()
                flash(f'Error actualizando permisos: {str(e)}', 'danger')
        
        return render_template(
            'user/permissions.html',
            user=user,
            countries=countries,
            modules=available_modules,
            permissions_by_country=permissions_by_country
        )
        
    except Exception as e:
        print(f"Error en manage_permissions: {e}")
        import traceback
        traceback.print_exc()
        flash('Error cargando la gestión de permisos.', 'danger')
        return redirect(url_for('user.list_user'))