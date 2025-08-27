from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_babel import _
from aclimate_v3_orm.services import MngAdmin2Service, MngAdmin1Service
from aclimate_v3_orm.schemas import Admin2Create, Admin2Update
from app.forms.adm2_form import Adm2Form

bp = Blueprint('adm2', __name__)
adm2_service = MngAdmin2Service()
adm1_service = MngAdmin1Service()

# Ruta: Listar y agregar con modal
@bp.route('/adm2', methods=['GET', 'POST'])
@login_required
def list_adm2():
    form = Adm2Form()
    form.admin_1_id.choices = [(a.id, a.name) for a in adm1_service.get_all()]

    if form.validate_on_submit():
        new_adm2 = Admin2Create(
            name=form.name.data,
            admin_1_id=form.admin_1_id.data,
            visible=form.visible.data,
            enable=form.enable.data
        )
        adm2_service.create(new_adm2)
        flash(_('División administrativa agregada correctamente.'), 'success')
        return redirect(url_for('adm2.list_adm2'))

    adm2_list = adm2_service.get_all()
    return render_template('adm2/list.html', adm2=adm2_list, form=form)

# Ruta: Agregar como pantalla independiente
@bp.route('/adm2/add', methods=['GET', 'POST'])
@login_required
def add_adm2():
    form = Adm2Form()
    form.admin_1_id.choices = [(a.id, a.name) for a in adm1_service.get_all()]

    if form.validate_on_submit():
        new_adm2 = Admin2Create(
            name=form.name.data,
            admin_1_id=form.admin_1_id.data,
            visible=form.visible.data,
            enable=form.enable.data
        )
        adm2_service.create(new_adm2)
        flash(_('División administrativa agregada correctamente.'), 'success')
        return redirect(url_for('adm2.list_adm2'))

    return render_template('adm2/add.html', form=form)

# Ruta: Editar Admin2
@bp.route('/adm2/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_adm2(id):
    adm = adm2_service.get_by_id(id)
    if not adm:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('adm2.list_adm2'))

    form = Adm2Form(obj=adm)
    form.admin_1_id.choices = [(a.id, a.name) for a in adm1_service.get_all(filters={"enable": True})]

    if request.method == 'GET':
        form.admin_1_id.data = adm.admin_1_id

    if form.validate_on_submit():
        update_data = Admin2Update(
            name=form.name.data,
            admin_1_id=form.admin_1_id.data,
            visible=form.visible.data,
            enable=form.enable.data
        )
        adm2_service.update(id=id, obj_in=update_data)
        flash(_('División administrativa actualizada.'), 'success')
        return redirect(url_for('adm2.list_adm2'))

    return render_template('adm2/edit.html', form=form, adm=adm)

# Ruta: Deshabilitar Admin2
@bp.route('/adm2/delete/<int:id>')
@login_required
def delete_adm2(id):
    if not adm2_service.delete(id):
        flash(_('No se pudo deshabilitar la división.'), 'danger')
    else:
        flash(_('División deshabilitada correctamente.'), 'warning')
    return redirect(url_for('adm2.list_adm2'))

# Ruta: Recuperar Admin2
@bp.route('/adm2/reset/<int:id>')
@login_required
def reset_adm2(id):
    adm = adm2_service.get_by_id(id)
    if not adm:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('adm2.list_adm2'))

    adm2_service.update(id=id, obj_in={"enable": True})
    flash(_('División administrativa reactivada.'), 'success')
    return redirect(url_for('adm2.list_adm2'))

@bp.route('/adm2/bulk_action', methods=['POST'])
@login_required
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    if not ids:
        flash('No se seleccionaron adm2.', 'warning')
        return redirect(url_for('adm2.list_adm2'))

    count = 0
    for loc_id in ids:
        try:
            loc_id_int = int(loc_id)
            if action == 'disable':
                if adm2_service.delete(loc_id_int):
                    count += 1
            elif action == 'recover':
                adm2_service.update(id=loc_id_int, obj_in={"enable": True})
                count += 1
        except Exception:
            continue

    if action == 'disable':
        flash(f'{count} adm2(s) deshabilitado(s).', 'warning')
    elif action == 'recover':
        flash(f'{count} adm2(s) recuperado(s).', 'success')
    else:
        flash('Acción no reconocida.', 'danger')
    return redirect(url_for('adm2.list_adm2'))