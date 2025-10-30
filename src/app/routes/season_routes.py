from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import _
from aclimate_v3_orm.services import MngSeasonService, MngLocationService, MngCropService
from aclimate_v3_orm.schemas import SeasonCreate, SeasonUpdate
from app.forms.season_form import SeasonForm
from app.decorators.permissions import require_module_access
from app.config.permissions import Module

bp = Blueprint('season', __name__)
season_service = MngSeasonService()
location_service = MngLocationService()
crop_service = MngCropService()

@bp.route('/season', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.CROP_DATA, permission_type='read')
def list_season():
    can_create = current_user.has_module_access(Module.CROP_DATA.value, 'create')
    
    form = SeasonForm()
    # Llenar dinámicamente las opciones de localidad y cultivo
    form.location_id.choices = [(l.id, l.name) for l in location_service.get_all()]
    form.crop_id.choices = [(c.id, c.name) for c in crop_service.get_all()]

    if form.validate_on_submit():
        if not can_create:
            flash(_('No tienes permiso para crear temporadas.'), 'danger')
            return redirect(url_for('season.list_season'))
            
        try:
            new_season = SeasonCreate(
                location_id=form.location_id.data,
                crop_id=form.crop_id.data,
                planting_start=form.planting_start.data,
                planting_end=form.planting_end.data,
                season_start=form.season_start.data,
                season_end=form.season_end.data,
                enable=True
            )
            season_service.create(new_season)
            flash(_('Temporada agregada correctamente.'), 'success')
            return redirect(url_for('season.list_season'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(_('Error al crear la temporada: %(error)s') % {'error': str(e)}, 'error')

    season_list = season_service.get_all()
    return render_template('season/list.html', seasons=season_list, form=form, can_create=can_create)

@bp.route('/season/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.CROP_DATA, permission_type='update')
def edit_season(id):
    season = season_service.get_by_id(id)
    if not season:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('season.list_season'))

    form = SeasonForm(obj=season)
    form.location_id.choices = [(l.id, l.name) for l in location_service.get_all()]
    form.crop_id.choices = [(c.id, c.name) for c in crop_service.get_all()]

    if request.method == 'GET':
        form.location_id.data = season.location_id
        form.crop_id.data = season.crop_id

    if form.validate_on_submit():
        try:
            update_data = SeasonUpdate(
                location_id=form.location_id.data,
                crop_id=form.crop_id.data,
                planting_start=form.planting_start.data,
                planting_end=form.planting_end.data,
                season_start=form.season_start.data,
                season_end=form.season_end.data,
                enable=form.enable.data
            )
            season_service.update(id=id, obj_in=update_data)
            flash(_('Temporada actualizada.'), 'success')
            return redirect(url_for('season.list_season'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(_('Error al actualizar la temporada: %(error)s') % {'error': str(e)}, 'error')

    return render_template('season/edit.html', form=form, season=season)

@bp.route('/season/delete/<int:id>')
@login_required
@require_module_access(Module.CROP_DATA, permission_type='delete')
def delete_season(id):
    if not season_service.delete(id):
        flash(_('No se pudo deshabilitar.'), 'danger')
    else:
        flash(_('Temporada deshabilitada.'), 'warning')
    return redirect(url_for('season.list_season'))

@bp.route('/season/reset/<int:id>')
@login_required
@require_module_access(Module.CROP_DATA, permission_type='update')
def reset_season(id):
    season = season_service.get_by_id(id)
    if not season:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('season.list_season'))

    season_service.update(id=id, obj_in={"enable": True})
    flash(_('Temporada reactivada.'), 'success')
    return redirect(url_for('season.list_season'))

@bp.route('/season/bulk_action', methods=['POST'])
@login_required
@require_module_access(Module.CROP_DATA, permission_type='delete')
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    if not ids:
        flash('No se seleccionaron temporadas.', 'warning')
        return redirect(url_for('season.list_season'))

    count = 0
    for season_id in ids:
        try:
            season_id_int = int(season_id)
            if action == 'disable':
                if season_service.delete(season_id_int):
                    count += 1
            elif action == 'recover':
                season_service.update(id=season_id_int, obj_in={"enable": True})
                count += 1
        except Exception:
            continue

    if action == 'disable':
        flash(f'{count} temporada(s) deshabilitada(s).', 'warning')
    elif action == 'recover':
        flash(f'{count} temporada(s) recuperada(s).', 'success')
    else:
        flash('Acción no reconocida.', 'danger')
    return redirect(url_for('season.list_season'))