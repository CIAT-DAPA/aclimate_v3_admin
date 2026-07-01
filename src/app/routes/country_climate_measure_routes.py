from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import _
from aclimate_v3_orm.services import MngCountryClimateMeasureService, MngCountryService, MngClimateMeasureService
from aclimate_v3_orm.schemas import CountryClimateMeasureCreate, CountryClimateMeasureUpdate
from app.forms.country_climate_measure_form import CountryClimateMeasureForm
from app.decorators.permissions import require_module_access
from app.config.permissions import Module

bp = Blueprint('country_climate_measure', __name__)
country_climate_measure_service = MngCountryClimateMeasureService()
country_service = MngCountryService()
measure_service = MngClimateMeasureService()


@bp.route('/country_climate_measure', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.CLIMATE_DATA, permission_type='read')
def list_country_climate_measure():
    can_create = current_user.has_module_access(Module.CLIMATE_DATA.value, 'create')

    form = CountryClimateMeasureForm()
    countries = country_service.get_all()
    measures = measure_service.get_all()
    form.country_id.choices = [(c.id, c.name) for c in countries]
    form.measure_id.choices = [(m.id, f"{m.name} ({m.short_name})") for m in measures]

    if form.validate_on_submit():
        if not can_create:
            flash(_('No tienes permiso para crear relaciones país-variable climática.'), 'danger')
            return redirect(url_for('country_climate_measure.list_country_climate_measure'))

        try:
            new_cm = CountryClimateMeasureCreate(
                country_id=int(form.country_id.data),
                measure_id=form.measure_id.data,
                spatial_forecast=form.spatial_forecast.data,
                spatial_climate=form.spatial_climate.data,
                location_forecast=form.location_forecast.data,
                location_climate=form.location_climate.data,
                description=form.description.data or None,
                store=form.store.data or None,
                workspace=form.workspace.data or None
            )
            country_climate_measure_service.create(new_cm)
            flash(_('Relación país-variable climática agregada correctamente.'), 'success')
            return redirect(url_for('country_climate_measure.list_country_climate_measure'))
        except Exception as e:
            flash(_('Error al crear la relación: ') + str(e), 'danger')
            cm_list = country_climate_measure_service.get_all()
            return render_template('country_climate_measure/list.html', country_climate_measures=cm_list, form=form, can_create=can_create)

    cm_list = country_climate_measure_service.get_all()
    return render_template('country_climate_measure/list.html', country_climate_measures=cm_list, form=form, can_create=can_create)


@bp.route('/country_climate_measure/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.CLIMATE_DATA, permission_type='update')
def edit_country_climate_measure(id):
    cm = country_climate_measure_service.get_by_id(id)
    if not cm:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('country_climate_measure.list_country_climate_measure'))

    form = CountryClimateMeasureForm(obj=cm)
    countries = country_service.get_all()
    measures = measure_service.get_all()
    form.country_id.choices = [(c.id, c.name) for c in countries]
    form.measure_id.choices = [(m.id, f"{m.name} ({m.short_name})") for m in measures]

    if request.method == 'GET':
        form.country_id.data = str(cm.country_id)
        form.measure_id.data = cm.measure_id

    if form.validate_on_submit():
        try:
            update_data = CountryClimateMeasureUpdate(
                country_id=int(form.country_id.data),
                measure_id=form.measure_id.data,
                spatial_forecast=form.spatial_forecast.data,
                spatial_climate=form.spatial_climate.data,
                location_forecast=form.location_forecast.data,
                location_climate=form.location_climate.data,
                description=form.description.data or None,
                store=form.store.data or None,
                workspace=form.workspace.data or None
            )
            country_climate_measure_service.update(id=id, obj_in=update_data)
            flash(_('Relación país-variable climática actualizada.'), 'success')
            return redirect(url_for('country_climate_measure.list_country_climate_measure'))
        except Exception as e:
            flash(_('Error al actualizar: ') + str(e), 'danger')
            return render_template('country_climate_measure/edit.html', form=form, country_climate_measure=cm)

    return render_template('country_climate_measure/edit.html', form=form, country_climate_measure=cm)


@bp.route('/country_climate_measure/delete/<int:id>')
@login_required
@require_module_access(Module.CLIMATE_DATA, permission_type='delete')
def delete_country_climate_measure(id):
    if not country_climate_measure_service.delete(id):
        flash(_('No se pudo eliminar.'), 'danger')
    else:
        flash(_('Relación país-variable climática eliminada.'), 'warning')
    return redirect(url_for('country_climate_measure.list_country_climate_measure'))


@bp.route('/country_climate_measure/bulk_action', methods=['POST'])
@login_required
@require_module_access(Module.CLIMATE_DATA, permission_type='delete')
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    if not ids:
        flash('No se seleccionaron relaciones.', 'warning')
        return redirect(url_for('country_climate_measure.list_country_climate_measure'))

    count = 0
    for cm_id in ids:
        try:
            cm_id_int = int(cm_id)
            if action == 'delete':
                if country_climate_measure_service.delete(cm_id_int):
                    count += 1
        except Exception:
            continue

    if action == 'delete':
        flash(f'{count} relación(es) eliminada(s).', 'warning')
    else:
        flash('Acción no reconocida.', 'danger')
    return redirect(url_for('country_climate_measure.list_country_climate_measure'))