from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_babel import _
from aclimate_v3_orm.services import MngSourceService
from aclimate_v3_orm.enums import SourceType
from aclimate_v3_orm.schemas import SourceCreate, SourceUpdate
from app.forms.source_form import SourceForm

bp = Blueprint('source', __name__)
source_service = MngSourceService()

@bp.route('/source', methods=['GET', 'POST'])
@login_required
def list_source():
    form = SourceForm()
    form.source_type.choices = [(SourceType.MANUAL.value, "Manual"), (SourceType.AUTOMATIC.value, "Automático")]

    if form.validate_on_submit():
        new_source = SourceCreate(
            name=form.name.data,
            source_type=form.source_type.data,
            enable=form.enable.data
        )
        source_service.create(new_source)
        flash(_('Fuente agregada correctamente.'), 'success')
        return redirect(url_for('source.list_source'))

    source_list = source_service.get_all()
    return render_template('source/list.html', sources=source_list, form=form)


@bp.route('/source/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_source(id):
    source = source_service.get_by_id(id)
    if not source:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('source.list_source'))

    form = SourceForm(obj=source)
    form.source_type.choices = [(SourceType.MANUAL.value, "Manual"), (SourceType.AUTOMATIC.value, "Automático")]

    if request.method == 'GET':
        form.source_type.data = source.source_type

    if form.validate_on_submit():
        update_data = SourceUpdate(
            name=form.name.data,
            source_type=form.source_type.data,
            enable=form.enable.data
        )

        source_service.update(id=id, obj_in=update_data)
        flash(_('Fuente actualizada.'), 'success')
        return redirect(url_for('source.list_source'))

    return render_template('source/edit.html', form=form, source=source)


@bp.route('/source/delete/<int:id>')
@login_required
def delete_source(id):
    if not source_service.delete(id):
        flash(_('No se pudo deshabilitar.'), 'danger')
    else:
        flash(_('Fuente deshabilitada.'), 'warning')
    return redirect(url_for('source.list_source'))


@bp.route('/source/reset/<int:id>')
@login_required
def reset_source(id):
    source = source_service.get_by_id(id)
    if not source:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('source.list_source'))

    source_service.update(id=id, obj_in={"enable": True})
    flash(_('Fuente reactivada.'), 'success')
    return redirect(url_for('source.list_source'))

@bp.route('/source/bulk_action', methods=['POST'])
@login_required
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    if not ids:
        flash('No se seleccionaron fuentes.', 'warning')
        return redirect(url_for('source.list_source'))

    count = 0
    for loc_id in ids:
        try:
            loc_id_int = int(loc_id)
            if action == 'disable':
                if source_service.delete(loc_id_int):
                    count += 1
            elif action == 'recover':
                source_service.update(id=loc_id_int, obj_in={"enable": True})
                count += 1
        except Exception:
            continue

    if action == 'disable':
        flash(f'{count} fuente(s) deshabilitada(s).', 'warning')
    elif action == 'recover':
        flash(f'{count} fuente(s) recuperada(s).', 'success')
    else:
        flash('Acción no reconocida.', 'danger')
    return redirect(url_for('source.list_source'))