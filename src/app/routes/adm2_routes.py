from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
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
        flash('División administrativa agregada correctamente.', 'success')
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
        flash('División administrativa agregada correctamente.', 'success')
        return redirect(url_for('adm2.list_adm2'))

    return render_template('adm2/add.html', form=form)

# Ruta: Editar Admin2
@bp.route('/adm2/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_adm2(id):
    adm = adm2_service.get_by_id(id)
    if not adm:
        flash('Registro no encontrado.', 'danger')
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
        flash('División administrativa actualizada.', 'success')
        return redirect(url_for('adm2.list_adm2'))

    return render_template('adm2/edit.html', form=form, adm=adm)

# Ruta: Deshabilitar Admin2
@bp.route('/adm2/delete/<int:id>')
@login_required
def delete_adm2(id):
    if not adm2_service.delete(id):
        flash('No se pudo deshabilitar la división.', 'danger')
    else:
        flash('División deshabilitada correctamente.', 'warning')
    return redirect(url_for('adm2.list_adm2'))

# Ruta: Recuperar Admin2
@bp.route('/adm2/reset/<int:id>')
@login_required
def reset_adm2(id):
    adm = adm2_service.get_by_id(id)
    if not adm:
        flash('Registro no encontrado.', 'danger')
        return redirect(url_for('adm2.list_adm2'))

    adm2_service.update(id=id, obj_in={"enable": True})
    flash('División administrativa reactivada.', 'success')
    return redirect(url_for('adm2.list_adm2'))