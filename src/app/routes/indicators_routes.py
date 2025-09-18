from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_babel import _
from aclimate_v3_orm.services import MngIndicatorService, MngIndicatorCategoryService
from aclimate_v3_orm.schemas import IndicatorCreate, IndicatorUpdate
from aclimate_v3_orm.enums import IndicatorsType
from app.forms.indicator_form import IndicatorForm

bp = Blueprint('indicator', __name__)
indicator_service = MngIndicatorService()
category_service = MngIndicatorCategoryService()

@bp.route('/indicator', methods=['GET', 'POST'])
@login_required
def list_indicator():
    form = IndicatorForm()
    # Llenar dinámicamente los tipos desde el Enum
    form.type.choices = [(cat.value, _(cat.value)) for cat in IndicatorsType]
    # Llenar dinámicamente las categorías
    categories = category_service.get_all()
    form.indicator_category_id.choices = [(cat.id, cat.name) for cat in categories]

    if form.validate_on_submit():
        new_indicator = IndicatorCreate(
            name=form.name.data,
            short_name=form.short_name.data,
            unit=form.unit.data,
            type=form.type.data,
            description=form.description.data,
            indicator_category_id=form.indicator_category_id.data,
            enable=True
        )
        indicator_service.create(new_indicator)
        flash(_('Indicador agregado correctamente.'), 'success')
        return redirect(url_for('indicator.list_indicator'))

    indicator_list = indicator_service.get_all()
    return render_template('indicator/list.html', indicators=indicator_list, form=form)

@bp.route('/indicator/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_indicator(id):
    indicator = indicator_service.get_by_id(id)
    if not indicator:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('indicator.list_indicator'))

    form = IndicatorForm(obj=indicator)
    # Llenar dinámicamente los tipos desde el Enum
    form.type.choices = [(cat.value, _(cat.value)) for cat in IndicatorsType]
    # Llenar dinámicamente las categorías
    categories = category_service.get_all()
    form.indicator_category_id.choices = [(cat.id, cat.name) for cat in categories]

    # Preseleccionar la categoría actual
    if request.method == 'GET' and indicator.indicator_category_id:
        form.indicator_category_id.data = indicator.indicator_category_id

    if form.validate_on_submit():
        update_data = IndicatorUpdate(
            name=form.name.data,
            short_name=form.short_name.data,
            type=form.type.data,
            unit=form.unit.data,
            description=form.description.data,
            indicator_category_id=form.indicator_category_id.data,
            enable=form.enable.data
        )
        indicator_service.update(id=id, obj_in=update_data)
        flash(_('Indicador actualizado.'), 'success')
        return redirect(url_for('indicator.list_indicator'))

    return render_template('indicator/edit.html', form=form, indicator=indicator)

@bp.route('/indicator/delete/<int:id>')
@login_required
def delete_indicator(id):
    if not indicator_service.delete(id):
        flash(_('No se pudo deshabilitar.'), 'danger')
    else:
        flash(_('Indicador deshabilitado.'), 'warning')
    return redirect(url_for('indicator.list_indicator'))

@bp.route('/indicator/reset/<int:id>')
@login_required
def reset_indicator(id):
    indicator = indicator_service.get_by_id(id)
    if not indicator:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('indicator.list_indicator'))

    indicator_service.update(id=id, obj_in={"enable": True})
    flash(_('Indicador reactivado.'), 'success')
    return redirect(url_for('indicator.list_indicator'))

@bp.route('/indicator/bulk_action', methods=['POST'])
@login_required
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    if not ids:
        flash('No se seleccionaron indicadores.', 'warning')
        return redirect(url_for('indicator.list_indicator'))

    count = 0
    for indicator_id in ids:
        try:
            indicator_id_int = int(indicator_id)
            if action == 'disable':
                if indicator_service.delete(indicator_id_int):
                    count += 1
            elif action == 'recover':
                indicator_service.update(id=indicator_id_int, obj_in={"enable": True})
                count += 1
        except Exception:
            continue

    if action == 'disable':
        flash(f'{count} indicador(es) deshabilitado(s).', 'warning')
    elif action == 'recover':
        flash(f'{count} indicador(es) recuperado(s).', 'success')
    else:
        flash('Acción no reconocida.', 'danger')
    return redirect(url_for('indicator.list_indicator'))