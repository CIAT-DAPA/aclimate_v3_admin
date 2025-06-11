from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_babel import _
from aclimate_v3_orm.services import MngAdmin1Service, MngCountryService
from aclimate_v3_orm.schemas import Admin1Create, Admin1Update
from app.forms.adm1_form import Adm1Form

bp = Blueprint('adm1', __name__)
adm1_service = MngAdmin1Service()
country_service = MngCountryService()

@bp.route('/adm1', methods=['GET', 'POST'])
@login_required
def list_adm1():
    form = Adm1Form()
    form.country_id.choices = [(c.id, c.name) for c in country_service.get_all()]

    if form.validate_on_submit():
        new_adm1 = Admin1Create(
            name=form.name.data,
            country_id=form.country_id.data,
            enable=form.enable.data
        )
        adm1_service.create(new_adm1)
        flash(_('División administrativa agregada correctamente.'), 'success')
        return redirect(url_for('adm1.list_adm1'))

    adm1_list = adm1_service.get_all()
    return render_template('adm1/list.html', adm1=adm1_list, form=form)


@bp.route('/adm1/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_adm1(id):
    adm = adm1_service.get_by_id(id)
    if not adm:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('adm1.list_adm1'))

    form = Adm1Form(obj=adm)
    form.country_id.choices = [(c.id, c.name) for c in country_service.get_all_enable()]
    
    if request.method == 'GET':
        form.country_id.data = adm.country_id

    if form.validate_on_submit():
        update_data = Admin1Update(
            name=form.name.data,
            country_id=form.country_id.data,
            enable=form.enable.data
        )

        adm1_service.update(id=id, obj_in=update_data)
        flash(_('División administrativa actualizada.'), 'success')
        return redirect(url_for('adm1.list_adm1'))

    return render_template('adm1/edit.html', form=form, adm=adm)


@bp.route('/adm1/delete/<int:id>')
@login_required
def delete_adm1(id):
    if not adm1_service.delete(id):
        flash(_('No se pudo deshabilitar.'), 'danger')
    else:
        flash(_('División deshabilitada.'), 'warning')
    return redirect(url_for('adm1.list_adm1'))


@bp.route('/adm1/reset/<int:id>')
@login_required
def reset_adm1(id):
    adm = adm1_service.get_by_id(id)
    if not adm:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('adm1.list_adm1'))

    adm1_service.update(id=id, obj_in={"enable": True})
    flash(_('División administrativa reactivada.'), 'success')
    return redirect(url_for('adm1.list_adm1'))
