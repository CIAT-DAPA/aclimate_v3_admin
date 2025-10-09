from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import _
from aclimate_v3_orm.services import MngCultivarService, MngCountryService, MngCropService
from aclimate_v3_orm.schemas import CultivarCreate, CultivarUpdate
from app.forms.cultivar_form import CultivarForm
from app.decorators.permissions import require_module_access
from app.config.permissions import Module

bp = Blueprint('cultivar', __name__)
cultivar_service = MngCultivarService()
country_service = MngCountryService()
crop_service = MngCropService()

@bp.route('/cultivar', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.CROP_DATA, permission_type='read')
def list_cultivar():
    can_create = current_user.has_module_access(Module.CROP_DATA.value, 'create')
    
    form = CultivarForm()
    # Llenar dinámicamente las opciones de país y cultivo
    form.country_id.choices = [(c.id, c.name) for c in country_service.get_all()]
    form.crop_id.choices = [(cr.id, cr.name) for cr in crop_service.get_all()]

    if form.validate_on_submit():
        if not can_create:
            flash(_('No tienes permiso para crear cultivares.'), 'danger')
            return redirect(url_for('cultivar.list_cultivar'))
            
        new_cultivar = CultivarCreate(
            country_id=form.country_id.data,
            crop_id=form.crop_id.data,
            name=form.name.data,
            sort_order=form.sort_order.data,
            rainfed=form.rainfed.data,
            enable=True
        )
        cultivar_service.create(new_cultivar)
        flash(_('Cultivar agregado correctamente.'), 'success')
        return redirect(url_for('cultivar.list_cultivar'))

    cultivar_list = cultivar_service.get_all()
    return render_template('cultivar/list.html', cultivars=cultivar_list, form=form, can_create=can_create)

@bp.route('/cultivar/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.CROP_DATA, permission_type='update')
def edit_cultivar(id):
    cultivar = cultivar_service.get_by_id(id)
    if not cultivar:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('cultivar.list_cultivar'))

    form = CultivarForm(obj=cultivar)
    form.country_id.choices = [(c.id, c.name) for c in country_service.get_all()]
    form.crop_id.choices = [(cr.id, cr.name) for cr in crop_service.get_all()]

    if request.method == 'GET':
        form.country_id.data = cultivar.country_id
        form.crop_id.data = cultivar.crop_id

    if form.validate_on_submit():
        update_data = CultivarUpdate(
            country_id=form.country_id.data,
            crop_id=form.crop_id.data,
            name=form.name.data,
            sort_order=form.sort_order.data,
            rainfed=form.rainfed.data,
            enable=form.enable.data
        )
        cultivar_service.update(id=id, obj_in=update_data)
        flash(_('Cultivar actualizado.'), 'success')
        return redirect(url_for('cultivar.list_cultivar'))

    return render_template('cultivar/edit.html', form=form, cultivar=cultivar)

@bp.route('/cultivar/delete/<int:id>')
@login_required
@require_module_access(Module.CROP_DATA, permission_type='delete')
def delete_cultivar(id):
    if not cultivar_service.delete(id):
        flash(_('No se pudo deshabilitar.'), 'danger')
    else:
        flash(_('Cultivar deshabilitado.'), 'warning')
    return redirect(url_for('cultivar.list_cultivar'))

@bp.route('/cultivar/reset/<int:id>')
@login_required
@require_module_access(Module.CROP_DATA, permission_type='update')
def reset_cultivar(id):
    cultivar = cultivar_service.get_by_id(id)
    if not cultivar:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('cultivar.list_cultivar'))

    cultivar_service.update(id=id, obj_in={"enable": True})
    flash(_('Cultivar reactivado.'), 'success')
    return redirect(url_for('cultivar.list_cultivar'))

@bp.route('/cultivar/bulk_action', methods=['POST'])
@login_required
@require_module_access(Module.CROP_DATA, permission_type='delete')
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    if not ids:
        flash('No se seleccionaron cultivares.', 'warning')
        return redirect(url_for('cultivar.list_cultivar'))

    count = 0
    for cultivar_id in ids:
        try:
            cultivar_id_int = int(cultivar_id)
            if action == 'disable':
                if cultivar_service.delete(cultivar_id_int):
                    count += 1
            elif action == 'recover':
                cultivar_service.update(id=cultivar_id_int, obj_in={"enable": True})
                count += 1
        except Exception:
            continue

    if action == 'disable':
        flash(f'{count} cultivar(es) deshabilitado(s).', 'warning')
    elif action == 'recover':
        flash(f'{count} cultivar(es) recuperado(s).', 'success')
    else:
        flash('Acción no reconocida.', 'danger')
    return redirect(url_for('cultivar.list_cultivar'))