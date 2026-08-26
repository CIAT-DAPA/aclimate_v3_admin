from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import _
from aclimate_v3_orm.services import MngCountryClimateMeasureService, MngCountryService, MngClimateMeasureService
from aclimate_v3_orm.schemas import CountryClimateMeasureCreate, CountryClimateMeasureUpdate
from aclimate_v3_orm.enums import Period
from app.forms.country_climate_measure_form import CountryClimateMeasureForm
from app.decorators.permissions import require_module_access
from app.config.permissions import Module

bp = Blueprint('country_climate_measure', __name__)
country_climate_measure_service = MngCountryClimateMeasureService()
country_service = MngCountryService()
measure_service = MngClimateMeasureService()


def _period_value(value):
    """Devuelve el valor string de un Period (funciona con enum o string)."""
    return value.value if hasattr(value, 'value') else value


def _build_spatial_climate_conf(req):
    """Construye spatial_climate_conf a partir de la grilla store/workspace por temporalidad.

    Solo se incluyen las temporalidades con Store o Workspace diligenciados.
    Devuelve None si no hay ninguna configuración.
    """
    conf = []
    for p in Period:
        store = (req.form.get(f'spatial_conf_store_{p.value}') or '').strip()
        workspace = (req.form.get(f'spatial_conf_workspace_{p.value}') or '').strip()
        if store or workspace:
            conf.append({
                'temporality': p.value,
                'store': store or None,
                'workspace': workspace or None,
            })
    return conf or None


def _spatial_conf_by_temporality(cm):
    """Mapa {temporality: {'store': ..., 'workspace': ...}} para precargar el formulario."""
    mapping = {}
    for item in (cm.spatial_climate_conf or []):
        if isinstance(item, dict):
            temp = item.get('temporality')
            store = item.get('store') or ''
            workspace = item.get('workspace') or ''
        else:
            temp = item.temporality
            store = item.store or ''
            workspace = item.workspace or ''
        mapping[_period_value(temp)] = {'store': store, 'workspace': workspace}
    return mapping


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
    form.location_climate_conf.choices = [(p.value, _(p.value)) for p in Period]

    if form.validate_on_submit():
        if not can_create:
            flash(_('No tienes permiso para crear relaciones país-variable climática.'), 'danger')
            return redirect(url_for('country_climate_measure.list_country_climate_measure'))

        spatial_climate_conf = _build_spatial_climate_conf(request)
        location_climate_conf = form.location_climate_conf.data or None

        if form.spatial_climate.data and not spatial_climate_conf:
            flash(_('La configuración de clima espacial es obligatoria si el clima espacial está activo.'), 'danger')
            cm_list = country_climate_measure_service.get_all()
            return render_template('country_climate_measure/list.html', country_climate_measures=cm_list, form=form, can_create=can_create, periods=list(Period), spatial_conf_by_temporality={})
        if form.location_climate.data and not location_climate_conf:
            flash(_('Debe seleccionar al menos una temporalidad para clima por ubicación.'), 'danger')
            cm_list = country_climate_measure_service.get_all()
            return render_template('country_climate_measure/list.html', country_climate_measures=cm_list, form=form, can_create=can_create, periods=list(Period), spatial_conf_by_temporality={})

        try:
            new_cm = CountryClimateMeasureCreate(
                country_id=int(form.country_id.data),
                measure_id=form.measure_id.data,
                spatial_forecast=form.spatial_forecast.data,
                spatial_climate=form.spatial_climate.data,
                location_forecast=form.location_forecast.data,
                location_climate=form.location_climate.data,
                spatial_climate_conf=spatial_climate_conf,
                location_climate_conf=location_climate_conf,
                description=form.description.data or None
            )
            country_climate_measure_service.create(new_cm)
            flash(_('Relación país-variable climática agregada correctamente.'), 'success')
            return redirect(url_for('country_climate_measure.list_country_climate_measure'))
        except Exception as e:
            flash(_('Error al crear la relación: ') + str(e), 'danger')
            cm_list = country_climate_measure_service.get_all()
            return render_template('country_climate_measure/list.html', country_climate_measures=cm_list, form=form, can_create=can_create, periods=list(Period), spatial_conf_by_temporality={})

    cm_list = country_climate_measure_service.get_all()
    return render_template('country_climate_measure/list.html', country_climate_measures=cm_list, form=form, can_create=can_create, periods=list(Period), spatial_conf_by_temporality={})


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
    form.location_climate_conf.choices = [(p.value, _(p.value)) for p in Period]

    spatial_conf_by_temporality = _spatial_conf_by_temporality(cm)

    if request.method == 'GET':
        form.country_id.data = str(cm.country_id)
        form.measure_id.data = cm.measure_id
        form.location_climate_conf.data = [_period_value(p) for p in (cm.location_climate_conf or [])]

    if form.validate_on_submit():
        spatial_climate_conf = _build_spatial_climate_conf(request)
        location_climate_conf = form.location_climate_conf.data or None

        if form.spatial_climate.data and not spatial_climate_conf:
            flash(_('La configuración de clima espacial es obligatoria si el clima espacial está activo.'), 'danger')
            return render_template('country_climate_measure/edit.html', form=form, country_climate_measure=cm, periods=list(Period), spatial_conf_by_temporality=spatial_conf_by_temporality)
        if form.location_climate.data and not location_climate_conf:
            flash(_('Debe seleccionar al menos una temporalidad para clima por ubicación.'), 'danger')
            return render_template('country_climate_measure/edit.html', form=form, country_climate_measure=cm, periods=list(Period), spatial_conf_by_temporality=spatial_conf_by_temporality)

        try:
            update_data = CountryClimateMeasureUpdate(
                spatial_forecast=form.spatial_forecast.data,
                spatial_climate=form.spatial_climate.data,
                location_forecast=form.location_forecast.data,
                location_climate=form.location_climate.data,
                spatial_climate_conf=spatial_climate_conf,
                location_climate_conf=location_climate_conf,
                description=form.description.data or None
            )
            country_climate_measure_service.update(id=id, obj_in=update_data)
            flash(_('Relación país-variable climática actualizada.'), 'success')
            return redirect(url_for('country_climate_measure.list_country_climate_measure'))
        except Exception as e:
            flash(_('Error al actualizar: ') + str(e), 'danger')
            return render_template('country_climate_measure/edit.html', form=form, country_climate_measure=cm, periods=list(Period), spatial_conf_by_temporality=spatial_conf_by_temporality)

    return render_template('country_climate_measure/edit.html', form=form, country_climate_measure=cm, periods=list(Period), spatial_conf_by_temporality=spatial_conf_by_temporality)


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