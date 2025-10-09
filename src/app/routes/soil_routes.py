from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import _
from aclimate_v3_orm.services import MngSoilService, MngCountryService, MngCropService
from aclimate_v3_orm.schemas import SoilCreate, SoilUpdate
from app.forms.soil_form import SoilForm
from app.decorators.permissions import require_module_access
from app.config.permissions import Module

bp = Blueprint('soil', __name__)
soil_service = MngSoilService()
country_service = MngCountryService()
crop_service = MngCropService()

@bp.route('/soil', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.CROP_DATA, permission_type='read')
def list_soil():
    can_create = current_user.has_module_access(Module.CROP_DATA.value, 'create')
    
    form = SoilForm()
    # Llenar dinámicamente las opciones de país y cultivo
    form.country_id.choices = [(c.id, c.name) for c in country_service.get_all()]
    form.crop_id.choices = [(cr.id, cr.name) for cr in crop_service.get_all()]

    if form.validate_on_submit():
        if not can_create:
            flash(_('No tienes permiso para crear suelos.'), 'danger')
            return redirect(url_for('soil.list_soil'))
            
        new_soil = SoilCreate(
            country_id=form.country_id.data,
            crop_id=form.crop_id.data,
            name=form.name.data,
            sort_order=form.sort_order.data,
            enable=True
        )
        soil_service.create(new_soil)
        flash(_('Suelo agregado correctamente.'), 'success')
        return redirect(url_for('soil.list_soil'))

    soil_list = soil_service.get_all()
    return render_template('soil/list.html', soils=soil_list, form=form, can_create=can_create)

@bp.route('/soil/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.CROP_DATA, permission_type='update')
def edit_soil(id):
    soil = soil_service.get_by_id(id)
    if not soil:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('soil.list_soil'))

    form = SoilForm(obj=soil)
    form.country_id.choices = [(c.id, c.name) for c in country_service.get_all()]
    form.crop_id.choices = [(cr.id, cr.name) for cr in crop_service.get_all()]

    if request.method == 'GET':
        form.country_id.data = soil.country_id
        form.crop_id.data = soil.crop_id

    if form.validate_on_submit():
        update_data = SoilUpdate(
            country_id=form.country_id.data,
            crop_id=form.crop_id.data,
            name=form.name.data,
            sort_order=form.sort_order.data,
            enable=form.enable.data
        )
        soil_service.update(id=id, obj_in=update_data)
        flash(_('Suelo actualizado.'), 'success')
        return redirect(url_for('soil.list_soil'))

    return render_template('soil/edit.html', form=form, soil=soil)

@bp.route('/soil/delete/<int:id>')
@login_required
@require_module_access(Module.CROP_DATA, permission_type='delete')
def delete_soil(id):
    if not soil_service.delete(id):
        flash(_('No se pudo deshabilitar.'), 'danger')
    else:
        flash(_('Suelo deshabilitado.'), 'warning')
    return redirect(url_for('soil.list_soil'))

@bp.route('/soil/reset/<int:id>')
@login_required
@require_module_access(Module.CROP_DATA, permission_type='update')
def reset_soil(id):
    soil = soil_service.get_by_id(id)
    if not soil:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('soil.list_soil'))

    soil_service.update(id=id, obj_in={"enable": True})
    flash(_('Suelo reactivado.'), 'success')
    return redirect(url_for('soil.list_soil'))

@bp.route('/soil/bulk_action', methods=['POST'])
@login_required
@require_module_access(Module.CROP_DATA, permission_type='delete')
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    if not ids:
        flash('No se seleccionaron suelos.', 'warning')
        return redirect(url_for('soil.list_soil'))

    count = 0
    for soil_id in ids:
        try:
            soil_id_int = int(soil_id)
            if action == 'disable':
                if soil_service.delete(soil_id_int):
                    count += 1
            elif action == 'recover':
                soil_service.update(id=soil_id_int, obj_in={"enable": True})
                count += 1
        except Exception:
            continue

    if action == 'disable':
        flash(f'{count} suelo(s) deshabilitado(s).', 'warning')
    elif action == 'recover':
        flash(f'{count} suelo(s) recuperado(s).', 'success')
    else:
        flash('Acción no reconocida.', 'danger')
    return redirect(url_for('soil.list_soil'))