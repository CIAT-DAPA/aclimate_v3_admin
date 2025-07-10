from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_babel import _
from aclimate_v3_orm.services import MngStressService
from aclimate_v3_orm.schemas import StressCreate, StressUpdate
from aclimate_v3_orm.enums import StressCategory
from app.forms.stress_form import StressForm

bp = Blueprint('stress', __name__)
stress_service = MngStressService()

@bp.route('/stress', methods=['GET', 'POST'])
@login_required
def list_stress():
    form = StressForm()
    # Llenar dinámicamente las categorías desde el Enum
    form.category.choices = [(cat.name, _(cat.value)) for cat in StressCategory]

    if form.validate_on_submit():
        new_stress = StressCreate(
            name=form.name.data,
            short_name=form.short_name.data,
            category=StressCategory[form.category.data],
            description=form.description.data,
        )
        stress_service.create(new_stress)
        flash(_('Estrés agregado correctamente.'), 'success')
        return redirect(url_for('stress.list_stress'))

    stress_list = stress_service.get_all()
    return render_template('stress/list.html', stresses=stress_list, form=form)

@bp.route('/stress/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_stress(id):
    stress = stress_service.get_by_id(id)
    if not stress:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('stress.list_stress'))

    form = StressForm(obj=stress)
    form.category.choices = [(cat.name, _(cat.value)) for cat in StressCategory]

    if request.method == 'GET':
        form.category.data = stress.category.name

    if form.validate_on_submit():
        update_data = StressUpdate(
            name=form.name.data,
            short_name=form.short_name.data,
            category=StressCategory[form.category.data],
            description=form.description.data,
        )
        stress_service.update(id=id, obj_in=update_data)
        flash(_('Estrés actualizado.'), 'success')
        return redirect(url_for('stress.list_stress'))

    return render_template('stress/edit.html', form=form, stress=stress)

@bp.route('/stress/delete/<int:id>')
@login_required
def delete_stress(id):
    if not stress_service.delete(id):
        flash(_('No se pudo deshabilitar.'), 'danger')
    else:
        flash(_('Estrés deshabilitado.'), 'warning')
    return redirect(url_for('stress.list_stress'))

@bp.route('/stress/reset/<int:id>')
@login_required
def reset_stress(id):
    stress = stress_service.get_by_id(id)
    if not stress:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('stress.list_stress'))

    stress_service.update(id=id, obj_in={"enable": True})
    flash(_('Estrés reactivado.'), 'success')
    return redirect(url_for('stress.list_stress'))

@bp.route('/stress/bulk_action', methods=['POST'])
@login_required
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    if not ids:
        flash('No se seleccionaron estreses.', 'warning')
        return redirect(url_for('stress.list_stress'))

    count = 0
    for stress_id in ids:
        try:
            stress_id_int = int(stress_id)
            if action == 'disable':
                if stress_service.delete(stress_id_int):
                    count += 1
            elif action == 'recover':
                stress_service.update(id=stress_id_int, obj_in={"enable": True})
                count += 1
        except Exception:
            continue

    if action == 'disable':
        flash(f'{count} estrés(es) deshabilitado(s).', 'warning')
    elif action == 'recover':
        flash(f'{count} estrés(es) recuperado(s).', 'success')
    else:
        flash('Acción no reconocida.', 'danger')
    return redirect(url_for('stress.list_stress'))