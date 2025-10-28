from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import _
from aclimate_v3_orm.services import MngClimateMeasureService
from aclimate_v3_orm.schemas import ClimateMeasureCreate, ClimateMeasureUpdate
from app.forms.climate_measure_form import ClimateMeasureForm
from app.decorators.permissions import require_module_access
from app.config.permissions import Module

bp = Blueprint('climate_measure', __name__)
measure_service = MngClimateMeasureService()


@bp.route('/climate_measure', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.CLIMATE_DATA, permission_type='read')
def list_climate_measure():
    can_create = current_user.has_module_access(Module.CLIMATE_DATA.value, 'create')
    form = ClimateMeasureForm()
    if form.validate_on_submit():
        if not can_create:
            flash(_('No tienes permiso para crear variables climáticas.'), 'danger')
            return redirect(url_for('climate_measure.list_climate_measure'))
        new_measure = ClimateMeasureCreate(
            name=form.name.data,
            short_name=form.short_name.data,
            unit=form.unit.data,
            description=form.description.data,
            enable=True
        )
        measure_service.create(new_measure)
        flash(_('Variable climática agregada correctamente.'), 'success')
        return redirect(url_for('climate_measure.list_climate_measure'))

    measures = measure_service.get_all()
    return render_template('climate_measure/list.html', measures=measures, form=form, can_create=can_create)


@bp.route('/climate_measure/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.CLIMATE_DATA, permission_type='update')
def edit_climate_measure(id):
    measure = measure_service.get_by_id(id)
    if not measure:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('climate_measure.list_climate_measure'))

    form = ClimateMeasureForm(obj=measure)
    if form.validate_on_submit():
        update_data = ClimateMeasureUpdate(
            name=form.name.data,
            short_name=form.short_name.data,
            unit=form.unit.data,
            description=form.description.data,
            enable=form.enable.data
        )
        measure_service.update(id=id, obj_in=update_data)
        flash(_('Variable climática actualizada.'), 'success')
        return redirect(url_for('climate_measure.list_climate_measure'))

    return render_template('climate_measure/edit.html', form=form, measure=measure)


@bp.route('/climate_measure/delete/<int:id>')
@login_required
@require_module_access(Module.CLIMATE_DATA, permission_type='delete')
def delete_climate_measure(id):
    if not measure_service.delete(id):
        flash(_('No se pudo deshabilitar.'), 'danger')
    else:
        flash(_('Variable climática deshabilitada.'), 'warning')
    return redirect(url_for('climate_measure.list_climate_measure'))


@bp.route('/climate_measure/reset/<int:id>')
@login_required
@require_module_access(Module.CLIMATE_DATA, permission_type='update')
def reset_climate_measure(id):
    measure = measure_service.get_by_id(id)
    if not measure:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('climate_measure.list_climate_measure'))

    measure_service.update(id=id, obj_in={"enable": True})
    flash(_('Variable climática reactivada.'), 'success')
    return redirect(url_for('climate_measure.list_climate_measure'))


@bp.route('/climate_measure/bulk_action', methods=['POST'])
@login_required
@require_module_access(Module.CLIMATE_DATA, permission_type='delete')
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    if not ids:
        flash('No se seleccionaron variables climáticas.', 'warning')
        return redirect(url_for('climate_measure.list_climate_measure'))

    count = 0
    for mid in ids:
        try:
            mid_int = int(mid)
            if action == 'disable':
                if measure_service.delete(mid_int):
                    count += 1
            elif action == 'recover':
                measure_service.update(id=mid_int, obj_in={"enable": True})
                count += 1
        except Exception:
            continue

    if action == 'disable':
        flash(f'{count} variable(s) climática(s) deshabilitada(s).', 'warning')
    elif action == 'recover':
        flash(f'{count} variable(s) climática(s) recuperada(s).', 'success')
    else:
        flash('Acción no reconocida.', 'danger')
    return redirect(url_for('climate_measure.list_climate_measure'))
