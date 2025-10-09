from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import _
from aclimate_v3_orm.services import MngPhenologicalStageService, MngCropService
from aclimate_v3_orm.schemas import PhenologicalStageCreate, PhenologicalStageUpdate
from app.forms.phenological_stage_form import PhenologicalStageForm
from app.decorators.permissions import require_module_access
from app.config.permissions import Module

bp = Blueprint('phenological_stage', __name__)
stage_service = MngPhenologicalStageService()
crop_service = MngCropService()

@bp.route('/phenological_stage', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.CROP_DATA, permission_type='read')
def list_phenological_stages():
    can_create = current_user.has_module_access(Module.CROP_DATA.value, 'create')
    
    form = PhenologicalStageForm()
    # Llenar dinámicamente las opciones de cultivos
    form.crop.choices = [(crop.id, crop.name) for crop in crop_service.get_all()]

    if form.validate_on_submit():
        if not can_create:
            flash(_('No tienes permiso para crear etapas fenológicas.'), 'danger')
            return redirect(url_for('phenological_stage.list_phenological_stages'))
            
        new_stage = PhenologicalStageCreate(
            crop_id=form.crop.data,
            name=form.name.data,
            short_name=form.short_name.data,
            description=form.description.data,
            order_stage=form.order_stage.data,
            duration_avg_day=form.duration_avg_day.data,
            enable=form.enable.data
        )
        stage_service.create(new_stage)
        flash(_('Etapa fenológica agregada correctamente.'), 'success')
        return redirect(url_for('phenological_stage.list_phenological_stages'))

    stages = stage_service.get_all()
    return render_template('phenological_stage/list.html', stages=stages, form=form, can_create=can_create)

@bp.route('/phenological_stage/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.CROP_DATA, permission_type='update')
def edit_phenological_stage(id):
    stage = stage_service.get_by_id(id)
    if not stage:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('phenological_stage.list_phenological_stages'))

    form = PhenologicalStageForm(obj=stage)
    # Llenar opciones de cultivos
    form.crop.choices = [(crop.id, crop.name) for crop in crop_service.get_all()]

    if request.method == 'GET':
        form.crop.data = stage.crop_id

    if form.validate_on_submit():
        update_data = PhenologicalStageUpdate(
            crop_id=form.crop.data,
            name=form.name.data,
            short_name=form.short_name.data,
            description=form.description.data,
            order_stage=form.order_stage.data,
            duration_avg_day=form.duration_avg_day.data,
            enable=form.enable.data
        )
        stage_service.update(id=id, obj_in=update_data)
        flash(_('Etapa fenológica actualizada.'), 'success')
        return redirect(url_for('phenological_stage.list_phenological_stages'))

    return render_template('phenological_stage/edit.html', form=form, stage=stage)

@bp.route('/phenological_stage/delete/<int:id>')
@login_required
@require_module_access(Module.CROP_DATA, permission_type='delete')
def delete_phenological_stage(id):
    if not stage_service.delete(id):
        flash(_('No se pudo deshabilitar.'), 'danger')
    else:
        flash(_('Etapa fenológica deshabilitada.'), 'warning')
    return redirect(url_for('phenological_stage.list_phenological_stages'))

@bp.route('/phenological_stage/reset/<int:id>')
@login_required
@require_module_access(Module.CROP_DATA, permission_type='update')
def reset_phenological_stage(id):
    stage = stage_service.get_by_id(id)
    if not stage:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('phenological_stage.list_phenological_stages'))

    stage_service.update(id=id, obj_in={"enable": True})
    flash(_('Etapa fenológica reactivada.'), 'success')
    return redirect(url_for('phenological_stage.list_phenological_stages'))

@bp.route('/phenological_stage/bulk_action', methods=['POST'])
@login_required
@require_module_access(Module.CROP_DATA, permission_type='delete')
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    if not ids:
        flash('No se seleccionaron etapas.', 'warning')
        return redirect(url_for('phenological_stage.list_phenological_stages'))

    count = 0
    for stage_id in ids:
        try:
            stage_id_int = int(stage_id)
            if action == 'disable':
                if stage_service.delete(stage_id_int):
                    count += 1
            elif action == 'recover':
                stage_service.update(id=stage_id_int, obj_in={"enable": True})
                count += 1
        except Exception:
            continue

    if action == 'disable':
        flash(f'{count} etapa(s) deshabilitada(s).', 'warning')
    elif action == 'recover':
        flash(f'{count} etapa(s) recuperada(s).', 'success')
    else:
        flash('Acción no reconocida.', 'danger')
    return redirect(url_for('phenological_stage.list_phenological_stages'))