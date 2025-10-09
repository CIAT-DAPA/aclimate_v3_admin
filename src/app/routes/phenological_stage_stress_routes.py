from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import _
from aclimate_v3_orm.services import PhenologicalStageStressService, MngPhenologicalStageService, MngStressService
from aclimate_v3_orm.schemas import PhenologicalStageStressCreate, PhenologicalStageStressUpdate
from app.forms.phenological_stage_stress_form import PhenologicalStageStressForm
from app.decorators.permissions import require_module_access
from app.config.permissions import Module

bp = Blueprint('phenological_stage_stress', __name__)
pss_service = PhenologicalStageStressService()
stage_service = MngPhenologicalStageService()
stress_service = MngStressService()

@bp.route('/phenological_stage_stress', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.CROP_DATA, permission_type='read')
def list_phenological_stage_stress():
    form = PhenologicalStageStressForm()
    # Llenar dinámicamente las opciones de estrés y etapa fenológica
    form.stress_id.choices = [(s.id, s.name) for s in stress_service.get_all_enable()]
    form.phenological_stage_id.choices = [(ps.id, ps.name) for ps in stage_service.get_all_enable()]

    if form.validate_on_submit():
        new_pss = PhenologicalStageStressCreate(
            stress_id=form.stress_id.data,
            phenological_stage_id=form.phenological_stage_id.data,
            max=form.max.data,
            min=form.min.data,
            enable=True
        )
        pss_service.create(new_pss)
        flash(_('Parámetro de estrés por etapa agregado correctamente.'), 'success')
        return redirect(url_for('phenological_stage_stress.list_phenological_stage_stress'))

    pss_list = pss_service.get_all()
    can_create = current_user.has_module_access(Module.CROP_DATA.value, 'create')
    return render_template('phenological_stage_stress/list.html', pss_list=pss_list, form=form, can_create=can_create)

@bp.route('/phenological_stage_stress/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.CROP_DATA, permission_type='update')
def edit_phenological_stage_stress(id):
    pss = pss_service.get_by_id(id)
    if not pss:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('phenological_stage_stress.list_phenological_stage_stress'))

    form = PhenologicalStageStressForm(obj=pss)
    form.stress_id.choices = [(s.id, s.name) for s in stress_service.get_all()]
    form.phenological_stage_id.choices = [(ps.id, ps.name) for ps in stage_service.get_all()]

    if request.method == 'GET':
        form.stress_id.data = pss.stress_id
        form.phenological_stage_id.data = pss.phenological_stage_id

    if form.validate_on_submit():
        update_data = PhenologicalStageStressUpdate(
            stress_id=form.stress_id.data,
            phenological_stage_id=form.phenological_stage_id.data,
            max=form.max.data,
            min=form.min.data,
            enable=form.enable.data
        )
        pss_service.update(id=id, obj_in=update_data)
        flash(_('Parámetro de estrés por etapa actualizado.'), 'success')
        return redirect(url_for('phenological_stage_stress.list_phenological_stage_stress'))

    return render_template('phenological_stage_stress/edit.html', form=form, pss=pss)

@bp.route('/phenological_stage_stress/delete/<int:id>')
@login_required
@require_module_access(Module.CROP_DATA, permission_type='delete')
def delete_phenological_stage_stress(id):
    if not pss_service.delete(id):
        flash(_('No se pudo deshabilitar.'), 'danger')
    else:
        flash(_('Parámetro deshabilitado.'), 'warning')
    return redirect(url_for('phenological_stage_stress.list_phenological_stage_stress'))

@bp.route('/phenological_stage_stress/reset/<int:id>')
@login_required
@require_module_access(Module.CROP_DATA, permission_type='update')
def reset_phenological_stage_stress(id):
    pss = pss_service.get_by_id(id)
    if not pss:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('phenological_stage_stress.list_phenological_stage_stress'))

    pss_service.update(id=id, obj_in={"enable": True})
    flash(_('Parámetro reactivado.'), 'success')
    return redirect(url_for('phenological_stage_stress.list_phenological_stage_stress'))

@bp.route('/phenological_stage_stress/bulk_action', methods=['POST'])
@login_required
@require_module_access(Module.CROP_DATA, permission_type='delete')
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    if not ids:
        flash('No se seleccionaron parámetros.', 'warning')
        return redirect(url_for('phenological_stage_stress.list_phenological_stage_stress'))

    count = 0
    for pss_id in ids:
        try:
            pss_id_int = int(pss_id)
            if action == 'disable':
                if pss_service.delete(pss_id_int):
                    count += 1
            elif action == 'recover':
                pss_service.update(id=pss_id_int, obj_in={"enable": True})
                count += 1
        except Exception:
            continue

    if action == 'disable':
        flash(f'{count} parámetro(s) deshabilitado(s).', 'warning')
    elif action == 'recover':
        flash(f'{count} parámetro(s) recuperado(s).', 'success')
    else:
        flash('Acción no reconocida.', 'danger')
    return redirect(url_for('phenological_stage_stress.list_phenological_stage_stress'))