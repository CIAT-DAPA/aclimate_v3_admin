from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_babel import _
from aclimate_v3_orm.services import MngCountryService
from aclimate_v3_orm.schemas import CountryCreate, CountryUpdate
from app.forms.country_form import CountryForm
from app.decorators.permissions import require_module_access
from app.config.permissions import Module

bp = Blueprint('country', __name__)
country_service = MngCountryService()

# Ruta: Lista de países
@bp.route('/country', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.GEOGRAPHIC, permission_type='read')
def list_country():
    can_create = current_user.has_module_access(Module.GEOGRAPHIC.value, 'create')
    
    form = CountryForm()
    if form.validate_on_submit():
        if not can_create:
            flash(_('No tienes permiso para crear países.'), 'danger')
            return redirect(url_for('country.list_country'))
            
        new_country = CountryCreate(
            name=form.name.data,
            iso2=form.iso2.data.upper(),
            enable=form.enable.data
        )
        country_service.create(new_country)
        flash(_('País agregado exitosamente.'), 'success')
        return redirect(url_for('country.list_country'))

    countries = country_service.get_all()
    return render_template('country/list.html', countries=countries, form=form, can_create=can_create)

# Ruta: Agregar país
@bp.route('/country/add', methods=['GET', 'POST'])
@login_required
def add_country():
    form = CountryForm()
    if form.validate_on_submit():
        try:
            country = CountryCreate(
                name=form.name.data,
                iso2=form.iso2.data.upper(),
                enable=form.enable.data
            )
            country_service.create(country)
            flash(_('País agregado exitosamente.'), 'success')
            return redirect(url_for('country.list_country'))
        except Exception as e:
            flash(_(f'Error adding country: {str(e)}'), 'danger')
    return render_template('country/add.html', form=form)

# Ruta: Editar país
@bp.route('/country/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.GEOGRAPHIC, permission_type='update')
def edit_country(id):
    existing = country_service.get_by_id(id)
    if not existing:
        flash(_('País no encontrado.'), 'danger')
        return redirect(url_for('country.list_country'))

    form = CountryForm(obj=existing)

    if form.validate_on_submit():
        update = CountryUpdate(
            name=form.name.data,
            iso2=form.iso2.data.upper(),
            enable=form.enable.data
        )

        flash(_('País actualizado correctamente.'), 'success')
        return redirect(url_for('country.list_country'))

    return render_template('country/edit.html', form=form, country=existing)

# Ruta: Eliminar (deshabilitar) país
@bp.route('/country/delete/<int:id>')
@login_required
@require_module_access(Module.GEOGRAPHIC, permission_type='delete')
def delete_country(id):
    if not country_service.delete(id):
        flash(_('No se pudo deshabilitar el país.'), 'danger')
    else:
        flash(_('País deshabilitado.'), 'warning')
    return redirect(url_for('country.list_country'))

# Ruta: Recuperar país
@bp.route('/country/reset/<int:id>')
@login_required
@require_module_access(Module.GEOGRAPHIC, permission_type='update')
def reset_country(id):
    existing = country_service.get_by_id(id)
    if not existing:
        flash(_('País no encontrado.'), 'danger')
        return redirect(url_for('country.list_country'))

    country_service.update(id=id, obj_in={"enable": True})
    flash(_('País recuperado.'), 'success')
    return redirect(url_for('country.list_country'))

@bp.route('/country/bulk_action', methods=['POST'])
@login_required
@require_module_access(Module.GEOGRAPHIC, permission_type='delete')
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    if not ids:
        flash('No se seleccionaron países.', 'warning')
        return redirect(url_for('country.list_country'))

    count = 0
    for loc_id in ids:
        try:
            loc_id_int = int(loc_id)
            if action == 'disable':
                if country_service.delete(loc_id_int):
                    count += 1
            elif action == 'recover':
                country_service.update(id=loc_id_int, obj_in={"enable": True})
                count += 1
        except Exception:
            continue

    if action == 'disable':
        flash(f'{count} país(es) deshabilitado(s).', 'warning')
    elif action == 'recover':
        flash(f'{count} país(es) recuperado(s).', 'success')
    else:
        flash('Acción no reconocida.', 'danger')
    return redirect(url_for('country.list_country'))