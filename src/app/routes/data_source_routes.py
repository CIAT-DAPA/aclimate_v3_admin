from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import _
from aclimate_v3_orm.services import MngDataSourceService, MngCountryService
from aclimate_v3_orm.schemas import DataSourceCreate, DataSourceUpdate
from app.forms.data_source_form import DataSourceForm
from app.decorators.permissions import require_module_access
from app.config.permissions import Module

bp = Blueprint('data_source', __name__)
data_source_service = MngDataSourceService()
country_service = MngCountryService()

@bp.route('/data_source', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.CONFIGURATION, permission_type='read')
def list_data_source():
    can_create = current_user.has_module_access(Module.CONFIGURATION.value, 'create')
    
    form = DataSourceForm()
    # Aquí deberías llenar dinámicamente los países
    form.country_id.choices = [(c.id, c.name) for c in country_service.get_all_enable()]

    if form.validate_on_submit():
        if not can_create:
            flash(_('No tienes permiso para crear fuentes de datos.'), 'danger')
            return redirect(url_for('data_source.list_data_source'))
            
        try:
            new_source = DataSourceCreate(
                country_id=form.country_id.data,
                name=form.name.data,
                description=form.description.data,
                type=form.type.data,
                enable=True,
                content=form.content.data
            )
            data_source_service.create(new_source)
            form.template.data = ''
            flash(_('Fuente de datos agregada correctamente.'), 'success')
            return redirect(url_for('data_source.list_data_source'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(_('Error al crear la fuente de datos: %(error)s', error=str(e)), 'danger')

    data_source_list = data_source_service.get_all()
    return render_template('data_source/list.html', data_sources=data_source_list, form=form, can_create=can_create)


@bp.route('/data_source/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.CONFIGURATION, permission_type='update')
def edit_data_source(id):
    data_source = data_source_service.get_by_id(id)
    if not data_source:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('data_source.list_source'))

    form = DataSourceForm(obj=data_source)
    form.country_id.choices = [(c.id, c.name) for c in country_service.get_all_enable()]
    form.template.data = ''

    if request.method == 'GET':
        form.type.data = data_source.type
        form.country_id.data = data_source.country_id

    if form.validate_on_submit():
        try:
            update_data = DataSourceUpdate(
                country_id=form.country_id.data,
                name=form.name.data,
                description=form.description.data,
                type=form.type.data,
                enable=form.enable.data,
                content=form.content.data
            )

            data_source_service.update(id=id, obj_in=update_data)
            flash(_('Fuente actualizada.'), 'success')
            return redirect(url_for('data_source.list_data_source'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(_('Error al actualizar la fuente de datos: %(error)s', error=str(e)), 'danger')

    return render_template('data_source/edit.html', form=form, data_source=data_source)


@bp.route('/data_source/delete/<int:id>')
@login_required
@require_module_access(Module.CONFIGURATION, permission_type='delete')
def delete_data_source(id):
    if not data_source_service.delete(id):
        flash(_('No se pudo deshabilitar.'), 'danger')
    else:
        flash(_('Fuente deshabilitada.'), 'warning')
    return redirect(url_for('data_source.list_data_source'))


@bp.route('/data_source/reset/<int:id>')
@login_required
@require_module_access(Module.CONFIGURATION, permission_type='update')
def reset_data_source(id):
    data_source = data_source_service.get_by_id(id)
    if not data_source:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('data_source.list_source'))

    data_source_service.update(id=id, obj_in={"enable": True})
    flash(_('Fuente reactivada.'), 'success')
    return redirect(url_for('data_source.list_data_source'))

@bp.route('/data_source/bulk_action', methods=['POST'])
@login_required
@require_module_access(Module.CONFIGURATION, permission_type='delete')
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    if not ids:
        flash('No se seleccionaron fuentes.', 'warning')
        return redirect(url_for('data_source.list_data_source'))

    count = 0
    for loc_id in ids:
        try:
            loc_id_int = int(loc_id)
            if action == 'disable':
                if data_source_service.delete(loc_id_int):
                    count += 1
            elif action == 'recover':
                data_source_service.update(id=loc_id_int, obj_in={"enable": True})
                count += 1
        except Exception:
            continue

    if action == 'disable':
        flash(f'{count} fuente(s) deshabilitada(s).', 'warning')
    elif action == 'recover':
        flash(f'{count} fuente(s) recuperada(s).', 'success')
    else:
        flash('Acción no reconocida.', 'danger')
    return redirect(url_for('data_source.list_data_source'))