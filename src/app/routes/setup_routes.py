from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_babel import _
from aclimate_v3_orm.services import MngSetupService, MngCultivarService, MngSoilService, MngSeasonService
from aclimate_v3_orm.schemas import SetupCreate, SetupUpdate
from app.forms.setup_form import SetupForm

bp = Blueprint('setup', __name__)
setup_service = MngSetupService()
cultivar_service = MngCultivarService()
soil_service = MngSoilService()
season_service = MngSeasonService()

@bp.route('/setup', methods=['GET', 'POST'])
@login_required
def list_setup():
    form = SetupForm()
    # Llenar dinámicamente las opciones de los select
    form.cultivar_id.choices = [(c.id, c.name) for c in cultivar_service.get_all_enable()]
    form.soil_id.choices = [(s.id, s.name) for s in soil_service.get_all_enable()]
    form.season_id.choices = [(se.id) for se in season_service.get_all_enable()]

    if form.validate_on_submit():
        new_setup = SetupCreate(
            cultivar_id=form.cultivar_id.data,
            soil_id=form.soil_id.data,
            season_id=form.season_id.data,
            frequency=form.frequency.data,
            enable=form.enable.data
        )
        setup_service.create(new_setup)
        flash(_('Configuración agregada correctamente.'), 'success')
        return redirect(url_for('setup.list_setup'))

    setup_list = setup_service.get_all()
    return render_template('setup/list.html', setup_list=setup_list, form=form)

@bp.route('/setup/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_setup(id):
    setup = setup_service.get_by_id(id)
    if not setup:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('setup.list_setup'))

    form = SetupForm(obj=setup)
    form.cultivar_id.choices = [(c.id, c.name) for c in cultivar_service.get_all()]
    form.soil_id.choices = [(s.id, s.name) for s in soil_service.get_all()]
    form.season_id.choices = [(se.id, se.name) for se in season_service.get_all()]

    if request.method == 'GET':
        form.cultivar_id.data = setup.cultivar_id
        form.soil_id.data = setup.soil_id
        form.season_id.data = setup.season_id

    if form.validate_on_submit():
        update_data = SetupUpdate(
            cultivar_id=form.cultivar_id.data,
            soil_id=form.soil_id.data,
            season_id=form.season_id.data,
            frequency=form.frequency.data,
            enable=form.enable.data
        )
        setup_service.update(id=id, obj_in=update_data)
        flash(_('Configuración actualizada.'), 'success')
        return redirect(url_for('setup.list_setup'))

    return render_template('setup/edit.html', form=form, setup=setup)

@bp.route('/setup/delete/<int:id>')
@login_required
def delete_setup(id):
    if not setup_service.delete(id):
        flash(_('No se pudo deshabilitar.'), 'danger')
    else:
        flash(_('Configuración deshabilitada.'), 'warning')
    return redirect(url_for('setup.list_setup'))

@bp.route('/setup/reset/<int:id>')
@login_required
def reset_setup(id):
    setup = setup_service.get_by_id(id)
    if not setup:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('setup.list_setup'))

    setup_service.update(id=id, obj_in={"enable": True})
    flash(_('Configuración reactivada.'), 'success')
    return redirect(url_for('setup.list_setup'))

@bp.route('/setup/bulk_action', methods=['POST'])
@login_required
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    if not ids:
        flash('No se seleccionaron configuraciones.', 'warning')
        return redirect(url_for('setup.list_setup'))

    count = 0
    for setup_id in ids:
        try:
            setup_id_int = int(setup_id)
            if action == 'disable':
                if setup_service.delete(setup_id_int):
                    count += 1
            elif action == 'recover':
                setup_service.update(id=setup_id_int, obj_in={"enable": True})
                count += 1
        except Exception:
            continue

    if action == 'disable':
        flash(f'{count} configuración(es) deshabilitada(s).', 'warning')
    elif action == 'recover':
        flash(f'{count} configuración(es) recuperada(s).', 'success')
    else:
        flash('Acción no reconocida.', 'danger')
    return redirect(url_for('setup.list_setup'))