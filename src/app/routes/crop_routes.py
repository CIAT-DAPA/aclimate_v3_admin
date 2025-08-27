from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_babel import _
from aclimate_v3_orm.services import MngCropService
from aclimate_v3_orm.schemas import CropCreate, CropUpdate
from app.forms.crop_form import CropForm

bp = Blueprint('crop', __name__)
crop_service = MngCropService()

@bp.route('/crop', methods=['GET', 'POST'])
@login_required
def list_crop():
    form = CropForm()

    if form.validate_on_submit():
        new_crop = CropCreate(
            name=form.name.data,
            enable=form.enable.data
        )
        crop_service.create(new_crop)
        flash(_('Cultivo agregado correctamente.'), 'success')
        return redirect(url_for('crop.list_crop'))

    crop_list = crop_service.get_all()
    return render_template('crop/list.html', crops=crop_list, form=form)

@bp.route('/crop/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_crop(id):
    crop = crop_service.get_by_id(id)
    if not crop:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('crop.list_crop'))

    form = CropForm(obj=crop)

    if form.validate_on_submit():
        update_data = CropUpdate(
            name=form.name.data,
            enable=form.enable.data
        )
        crop_service.update(id=id, obj_in=update_data)
        flash(_('Cultivo actualizado.'), 'success')
        return redirect(url_for('crop.list_crop'))

    return render_template('crop/edit.html', form=form, crop=crop)

@bp.route('/crop/delete/<int:id>')
@login_required
def delete_crop(id):
    if not crop_service.delete(id):
        flash(_('No se pudo deshabilitar.'), 'danger')
    else:
        flash(_('Cultivo deshabilitado.'), 'warning')
    return redirect(url_for('crop.list_crop'))

@bp.route('/crop/reset/<int:id>')
@login_required
def reset_crop(id):
    crop = crop_service.get_by_id(id)
    if not crop:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('crop.list_crop'))

    crop_service.update(id=id, obj_in={"enable": True})
    flash(_('Cultivo reactivado.'), 'success')
    return redirect(url_for('crop.list_crop'))

@bp.route('/crop/bulk_action', methods=['POST'])
@login_required
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    if not ids:
        flash('No se seleccionaron cultivos.', 'warning')
        return redirect(url_for('crop.list_crop'))

    count = 0
    for crop_id in ids:
        try:
            crop_id_int = int(crop_id)
            if action == 'disable':
                if crop_service.delete(crop_id_int):
                    count += 1
            elif action == 'recover':
                crop_service.update(id=crop_id_int, obj_in={"enable": True})
                count += 1
        except Exception:
            continue

    if action == 'disable':
        flash(f'{count} cultivo(s) deshabilitado(s).', 'warning')
    elif action == 'recover':
        flash(f'{count} cultivo(s) recuperado(s).', 'success')
    else:
        flash('Acción no reconocida.', 'danger')
    return redirect(url_for('crop.list_crop'))