from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import _
from aclimate_v3_orm_frontend.services import AppService
from aclimate_v3_orm_frontend.schemas import AppCreate, AppUpdate
from app.forms.app_form import AppForm
from app.decorators.permissions import require_module_access
from app.config.permissions import Module

bp = Blueprint('app', __name__)
app_service = AppService()

@bp.route('/app', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.CONFIGURATION, permission_type='read')
def list_app():
    can_create = current_user.has_module_access(Module.CONFIGURATION.value, 'create')
    
    form = AppForm()

    if form.validate_on_submit():
        if not can_create:
            flash(_('No tienes permiso para crear aplicaciones.'), 'danger')
            return redirect(url_for('app.list_app'))
        
        try:
            new_app = AppCreate(
                name=form.name.data,
                country_ext_id=form.country_ext_id.data,
                enable=True
            )
            app_service.create(new_app)
            flash(_('Aplicación agregada correctamente.'), 'success')
            return redirect(url_for('app.list_app'))
        except Exception as e:
            flash(_('Error al crear la aplicación: ') + str(e), 'danger')

    app_list = app_service.get_all()
    return render_template('app/list.html', apps=app_list, form=form, can_create=can_create)

@bp.route('/app/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.CONFIGURATION, permission_type='update')
def edit_app(id):
    app = app_service.get_by_id(id)
    if not app:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('app.list_app'))

    form = AppForm(obj=app)

    if request.method == 'GET':
        form.name.data = app.name
        form.country_ext_id.data = app.country_ext_id
        form.enable.data = app.enable

    if form.validate_on_submit():
        try:
            update_data = AppUpdate(
                name=form.name.data,
                country_ext_id=form.country_ext_id.data,
                enable=form.enable.data
            )
            app_service.update(id=id, obj_in=update_data)
            flash(_('Aplicación actualizada.'), 'success')
            return redirect(url_for('app.list_app'))
        except Exception as e:
            flash(_('Error al actualizar: ') + str(e), 'danger')
            return render_template('app/edit.html', form=form, app=app)

    return render_template('app/edit.html', form=form, app=app)

@bp.route('/app/delete/<int:id>')
@login_required
@require_module_access(Module.CONFIGURATION, permission_type='delete')
def delete_app(id):
    try:
        if not app_service.delete(id):
            flash(_('No se pudo deshabilitar.'), 'danger')
        else:
            flash(_('Aplicación deshabilitada.'), 'warning')
    except Exception as e:
        flash(_('Error al deshabilitar: ') + str(e), 'danger')
    return redirect(url_for('app.list_app'))

@bp.route('/app/reset/<int:id>')
@login_required
@require_module_access(Module.CONFIGURATION, permission_type='update')
def reset_app(id):
    app = app_service.get_by_id(id)
    if not app:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('app.list_app'))

    try:
        app_service.update(id=id, obj_in={"enable": True})
        flash(_('Aplicación reactivada.'), 'success')
    except Exception as e:
        flash(_('Error al reactivar: ') + str(e), 'danger')
    return redirect(url_for('app.list_app'))

@bp.route('/app/bulk_action', methods=['POST'])
@login_required
@require_module_access(Module.CONFIGURATION, permission_type='delete')
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    if not ids:
        flash(_('No se seleccionaron aplicaciones.'), 'warning')
        return redirect(url_for('app.list_app'))

    count = 0
    for app_id in ids:
        try:
            app_id_int = int(app_id)
            if action == 'disable':
                if app_service.delete(app_id_int):
                    count += 1
            elif action == 'recover':
                app_service.update(id=app_id_int, obj_in={"enable": True})
                count += 1
        except Exception:
            continue

    if action == 'disable':
        flash(_(f'{count} aplicación(es) deshabilitada(s).'), 'warning')
    elif action == 'recover':
        flash(_(f'{count} aplicación(es) recuperada(s).'), 'success')
    else:
        flash(_('Acción no reconocida.'), 'danger')
    return redirect(url_for('app.list_app'))
