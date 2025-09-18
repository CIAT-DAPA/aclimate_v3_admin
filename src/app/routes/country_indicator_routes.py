from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_babel import _
from aclimate_v3_orm.services import MngCountryIndicatorService, MngCountryService, MngIndicatorService
from aclimate_v3_orm.schemas import CountryIndicatorCreate, CountryIndicatorUpdate
from app.forms.country_indicator_form import CountryIndicatorForm
import json

bp = Blueprint('country_indicator', __name__)
country_indicator_service = MngCountryIndicatorService()
country_service = MngCountryService()
indicator_service = MngIndicatorService()

@bp.route('/country_indicator', methods=['GET', 'POST'])
@login_required
def list_country_indicator():
    form = CountryIndicatorForm()
    countries = country_service.get_all()
    indicators = indicator_service.get_all()
    form.country_id.choices = [(c.id, c.name) for c in countries]
    form.indicator_id.choices = [(i.id, i.name) for i in indicators]

    if form.validate_on_submit():
        criteria_data = None
        if form.criteria.data:
            try:
                criteria_data = json.loads(form.criteria.data)
            except Exception:
                criteria_data = None  # O puedes manejar el error como prefieras

        new_ci = CountryIndicatorCreate(
            country_id=int(form.country_id.data),
            indicator_id=form.indicator_id.data,
            spatial_forecast=form.spatial_forecast.data,
            spatial_climate=form.spatial_climate.data,
            location_forecast=form.location_forecast.data,
            location_climate=form.location_climate.data,
            criteria=criteria_data
        )
        country_indicator_service.create(new_ci)
        flash(_('Relación país-indicador agregada correctamente.'), 'success')
        return redirect(url_for('country_indicator.list_country_indicator'))

    ci_list = country_indicator_service.get_all()
    return render_template('country_indicator/list.html', country_indicators=ci_list, form=form)

@bp.route('/country_indicator/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_country_indicator(id):
    ci = country_indicator_service.get_by_id(id)
    if not ci:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('country_indicator.list_country_indicator'))

    form = CountryIndicatorForm(obj=ci)
    countries = country_service.get_all()
    indicators = indicator_service.get_all()
    form.country_id.choices = [(c.id, c.name) for c in countries]
    form.indicator_id.choices = [(i.id, i.name) for i in indicators]

    if request.method == 'GET':
        form.country_id.data = str(ci.country_id)
        form.indicator_id.data = ci.indicator_id

    if form.validate_on_submit():
        update_data = CountryIndicatorUpdate(
            country_id=int(form.country_id.data),
            indicator_id=form.indicator_id.data,
            spatial_forecast=form.spatial_forecast.data,
            spatial_climate=form.spatial_climate.data,
            location_forecast=form.location_forecast.data,
            location_climate=form.location_climate.data,
            criteria=form.criteria.data
        )
        country_indicator_service.update(id=id, obj_in=update_data)
        flash(_('Relación país-indicador actualizada.'), 'success')
        return redirect(url_for('country_indicator.list_country_indicator'))

    return render_template('country_indicator/edit.html', form=form, country_indicator=ci)

@bp.route('/country_indicator/delete/<int:id>')
@login_required
def delete_country_indicator(id):
    if not country_indicator_service.delete(id):
        flash(_('No se pudo eliminar.'), 'danger')
    else:
        flash(_('Relación país-indicador eliminada.'), 'warning')
    return redirect(url_for('country_indicator.list_country_indicator'))

@bp.route('/country_indicator/reset/<int:id>')
@login_required
def reset_country_indicator(id):
    ci = country_indicator_service.get_by_id(id)
    if not ci:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('country_indicator.list_country_indicator'))

    country_indicator_service.update(id=id, obj_in={"enable": True})
    flash(_('Relación país-indicador reactivada.'), 'success')
    return redirect(url_for('country_indicator.list_country_indicator'))

@bp.route('/country_indicator/bulk_action', methods=['POST'])
@login_required
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    if not ids:
        flash('No se seleccionaron relaciones.', 'warning')
        return redirect(url_for('country_indicator.list_country_indicator'))

    count = 0
    for ci_id in ids:
        try:
            ci_id_int = int(ci_id)
            if action == 'disable':
                if country_indicator_service.delete(ci_id_int):
                    count += 1
            elif action == 'recover':
                country_indicator_service.update(id=ci_id_int, obj_in={"enable": True})
                count += 1
        except Exception:
            continue

    if action == 'disable':
        flash(f'{count} relación(es) deshabilitada(s).', 'warning')
    elif action == 'recover':
        flash(f'{count} relación(es) recuperada(s).', 'success')
    else:
        flash('Acción no reconocida.', 'danger')
    return redirect(url_for('country_indicator.list_country_indicator'))