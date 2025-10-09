import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import _
from werkzeug.utils import secure_filename
from flask import current_app
from aclimate_v3_orm.services import MngSetupService, MngCultivarService, MngSoilService, MngSeasonService, MngConfigurationFileService
from aclimate_v3_orm.schemas import SetupCreate, SetupUpdate, ConfigurationFileCreate  
from app.forms.setup_form import SetupForm
from app.decorators.permissions import require_module_access
from app.config.permissions import Module
from config import Config


bp = Blueprint('setup', __name__)
setup_service = MngSetupService()
cultivar_service = MngCultivarService()
soil_service = MngSoilService()
season_service = MngSeasonService()

@bp.route('/setup', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.CROP_DATA, permission_type='read')
def list_setup():
    can_create = current_user.has_module_access(Module.CROP_DATA.value, 'create')
    
    form = SetupForm()
    # Llenar dinámicamente las opciones de los select
    form.cultivar_id.choices = [(c.id, c.name) for c in cultivar_service.get_all_enable()]
    form.soil_id.choices = [(s.id, s.name) for s in soil_service.get_all_enable()]
    form.season_id.choices = [(se.id) for se in season_service.get_all_enable()]

    if form.validate_on_submit():
        if not can_create:
            flash(_('No tienes permiso para crear configuraciones.'), 'danger')
            return redirect(url_for('setup.list_setup'))
            
        new_setup = SetupCreate(
            cultivar_id=form.cultivar_id.data,
            soil_id=form.soil_id.data,
            season_id=form.season_id.data,
            frequency=form.frequency.data,
            enable=True
        )
         # Crear el setup
        created_setup = setup_service.create(new_setup)
        
        # Manejar archivos subidos
        if form.config_files.data:
            save_uploaded_files(form.config_files.data, created_setup.id)
            flash(_('Archivos subidos correctamente.'), 'success')

        flash(_('Configuración agregada correctamente.'), 'success')
        return redirect(url_for('setup.list_setup'))

    setup_list = setup_service.get_all()
    return render_template('setup/list.html', setup_list=setup_list, form=form, can_create=can_create)

@bp.route('/setup/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.CROP_DATA, permission_type='update')
def edit_setup(id):
    setup = setup_service.get_by_id(id)
    if not setup:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('setup.list_setup'))

    form = SetupForm(obj=setup)
    form.cultivar_id.choices = [(c.id, c.name) for c in cultivar_service.get_all()]
    form.soil_id.choices = [(s.id, s.name) for s in soil_service.get_all()]
    form.season_id.choices = [(se.id) for se in season_service.get_all_enable()]

    if request.method == 'GET':
        form.cultivar_id.data = setup.cultivar_id
        form.soil_id.data = setup.soil_id
        form.season_id.data = setup.season_id

    if form.validate_on_submit():
        update_data = SetupUpdate(
            cultivar_id=form.cultivar_id.data,
            soil_id=form.soil_id.data,
            season_id=form.season_id.data,
            frequency=form.frequency.data
        )
        setup_service.update(id=id, obj_in=update_data)
        # Manejar archivos subidos
        if form.config_files.data:
            save_uploaded_files(form.config_files.data, setup.id)
            flash(_('Archivos subidos correctamente.'), 'success')
            
        flash(_('Configuración actualizada.'), 'success')
        return redirect(url_for('setup.list_setup'))

    return render_template('setup/edit.html', form=form, setup=setup)

@bp.route('/setup/delete/<int:id>')
@login_required
@require_module_access(Module.CROP_DATA, permission_type='delete')
def delete_setup(id):
    if not setup_service.delete(id):
        flash(_('No se pudo deshabilitar.'), 'danger')
    else:
        flash(_('Configuración deshabilitada.'), 'warning')
    return redirect(url_for('setup.list_setup'))

@bp.route('/setup/delete_file/<int:file_id>', methods=['POST'])
@login_required
@require_module_access(Module.CROP_DATA, permission_type='delete')
def delete_file(file_id):
    file_service = MngConfigurationFileService()
    file = file_service.get_by_id(file_id)
    
    if file:
        # Eliminar archivo físico
        try:
            file_path = os.path.join(Config.UPLOAD_FOLDER, file.path)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            current_app.logger.error(f"Error deleting file: {str(e)}")
        
        # Eliminar registro de la base de datos
        file_service.delete(file_id)
        flash(_('Archivo eliminado correctamente.'), 'success')
    else:
        flash(_('Archivo no encontrado.'), 'danger')
    
    return redirect(url_for('setup.edit_setup', id=file.setup_id))

def save_uploaded_files(files, setup_id):
    file_service = MngConfigurationFileService()
    upload_folder = Config.UPLOAD_FOLDER

    # Crear carpeta específica para el setup
    setup_folder = os.path.join(upload_folder, str(setup_id))
    os.makedirs(setup_folder, exist_ok=True)

    for file in files:
        if file.filename == '':
            continue

        filename = secure_filename(file.filename)
        relative_path = os.path.join(str(setup_id), filename)
        file_data = ConfigurationFileCreate(
            setup_id=setup_id,
            name=file.filename,  # Nombre original
            path=relative_path,
            enable=True
        )

        try:
            # Validar el archivo antes de guardarlo
            file_service.validate_file(file_data)
        except Exception as e:
            print(f"Error validating file {filename}: {str(e)}")
            flash(str(e), 'danger')
            continue  # No guardar archivo ni registro si falla la validación

        file_path = os.path.join(setup_folder, filename)
        file.save(file_path)
        file_service.create(file_data)

@bp.route('/setup/reset/<int:id>')
@login_required
@require_module_access(Module.CROP_DATA, permission_type='update')
def reset_setup(id):
    setup = setup_service.get_by_id(id)
    if not setup:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('setup.list_setup'))

    setup_service.update(id=id, obj_in={"enable": True})
    flash(_('Configuración reactivada.'), 'success')
    return redirect(url_for('setup.list_setup'))

@bp.route('/setup/bulk_action', methods=['POST'])
@login_required
@require_module_access(Module.CROP_DATA, permission_type='delete')
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    if not ids:
        flash('No se seleccionaron configuraciones.', 'warning')
        return redirect(url_for('setup.list_setup'))

    count = 0
    for setup_id in ids:
        try:
            setup_id_int = int(setup_id)
            if action == 'disable':
                if setup_service.delete(setup_id_int):
                    count += 1
            elif action == 'recover':
                setup_service.update(id=setup_id_int, obj_in={"enable": True})
                count += 1
        except Exception:
            continue

    if action == 'disable':
        flash(f'{count} configuración(es) deshabilitada(s).', 'warning')
    elif action == 'recover':
        flash(f'{count} configuración(es) recuperada(s).', 'success')
    else:
        flash('Acción no reconocida.', 'danger')
    return redirect(url_for('setup.list_setup'))