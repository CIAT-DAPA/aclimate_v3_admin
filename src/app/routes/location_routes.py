from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from aclimate_v3_orm.services import MngAdmin2Service, MngAdmin1Service, MngLocationService, MngCountryService, MngSourceService
from aclimate_v3_orm.schemas import LocationCreate, LocationUpdate
from app.forms.location_form import LocationForm
from app.decorators.permissions import require_module_access
from app.config.permissions import Module

bp = Blueprint('location', __name__)
country_service = MngCountryService()
location_service = MngLocationService()
adm2_service = MngAdmin2Service()
adm1_service = MngAdmin1Service()
source_service = MngSourceService()


# Ruta: Listar y agregar con modal
@bp.route('/location', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.GEOGRAPHIC, permission_type='read')
def list_location():
    can_create = current_user.has_module_access(Module.GEOGRAPHIC.value, 'create')
    
    form = LocationForm()
    form.country.choices = [(0, '---------')] + [(a.id, a.name) for a in country_service.get_all()]
    # Solo la opción vacía para selects dependientes
    form.admin_1_id.choices = [(0, '---------')]
    form.admin_2_id.choices = [(0, '---------')]
    form.source_id.choices = [(0, '---------')] + [(s.id, s.name) for s in source_service.get_all()]

    # Si es POST, se poblan los choices según lo enviado (para que WTForms valide correctamente)
    if form.country.data:
        form.admin_1_id.choices = [(0, '---------')] + [(a.id, a.name) for a in adm1_service.get_by_country_id(form.country.data)]
    if form.admin_1_id.data:
        form.admin_2_id.choices = [(0, '---------')] + [(a.id, a.name) for a in adm2_service.get_by_admin1_id(form.admin_1_id.data)]

    if form.validate_on_submit():
        if not can_create:
            flash('No tienes permiso para crear locaciones.', 'danger')
            return redirect(url_for('location.list_location'))
            
        new_location = LocationCreate(
            admin_2_id=form.admin_2_id.data,
            source_id=form.source_id.data,
            name=form.ubi.data,
            ext_id=form.ubi.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            altitude=form.altitude.data,
            enable=True  
            )
        location_service.create(new_location)
        flash('Locación agregada correctamente.', 'success')
        return redirect(url_for('location.list_location'))

    location_list = location_service.get_all()
    return render_template('location/list.html', location=location_list, form=form, can_create=can_create)

# Ruta: Agregar como pantalla independiente
@bp.route('/location/add', methods=['GET', 'POST'])
@login_required
def add_location():
    form = LocationForm()
    form.country.choices = [(a.id, a.name) for a in country_service.get_all()]

    if form.validate_on_submit():
        new_location = LocationCreate(
            admin_2_id=form.admin_2_id.data,
            source_id=form.source.data,
            name=form.ubi.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            altitude=form.altitude.data,
            visible=form.visible.data   
            )
        location_service.create(new_location)
        flash('Locación agregada correctamente.', 'success')
        return redirect(url_for('location.list_location'))

    return render_template('location/add.html', form=form)

# Ruta: Editar locación
@bp.route('/location/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.GEOGRAPHIC, permission_type='update')
def edit_location(id):
    loc = location_service.get_by_id(id)
    if not loc:
        flash('Registro no encontrado.', 'danger')
        return redirect(url_for('location.list_location'))

    form = LocationForm(obj=loc)
    form.country.choices = [(0, '---------')] + [(a.id, a.name) for a in country_service.get_all()]
    # Solo la opción vacía para selects dependientes
    form.admin_1_id.choices = [(0, '---------')]
    form.admin_2_id.choices = [(0, '---------')]
    form.source_id.choices = [(0, '---------')] + [(s.id, s.name) for s in source_service.get_all()]
    
    # Si es POST, se poblan los choices según lo enviado (para que WTForms valide correctamente)
    if form.country.data:
        form.admin_1_id.choices = [(0, '---------')] + [(a.id, a.name) for a in adm1_service.get_by_country_id(form.country.data)]
    if form.admin_1_id.data:
        form.admin_2_id.choices = [(0, '---------')] + [(a.id, a.name) for a in adm2_service.get_by_admin1_id(form.admin_1_id.data)]


    if request.method == 'GET':
        form.country.data = loc.country
        form.ubi.data = loc.name

    if form.validate_on_submit():
        update_data = LocationUpdate(
            admin_2_id=form.admin_2_id.data,
            source_id=form.source_id.data,
            name=form.ubi.data,
            ext_id=form.ubi.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            altitude=form.altitude.data,
            enable=True   
            )
        location_service.update(id=id, obj_in=update_data)
        flash('Locación actualizada.', 'success')
        return redirect(url_for('location.list_location'))
    print(form)
    return render_template('location/edit.html', form=form, loc=loc)

# Ruta: Deshabilitar locacion
@bp.route('/location/delete/<int:id>')
@login_required
@require_module_access(Module.GEOGRAPHIC, permission_type='delete')
def delete_location(id):
    if not location_service.delete(id):
        flash('No se pudo deshabilitar la locación.', 'danger')
    else:
        flash('Locación deshabilitada correctamente.', 'warning')
    return redirect(url_for('location.list_location'))

# Ruta: Recuperar locacion
@bp.route('/location/reset/<int:id>')
@login_required
@require_module_access(Module.GEOGRAPHIC, permission_type='update')
def reset_location(id):
    loc = location_service.get_by_id(id)
    if not loc:
        flash('Registro no encontrado.', 'danger')
        return redirect(url_for('location.list_location'))

    location_service.update(id=id, obj_in={"enable": True})
    flash('Locación reactivada.', 'success')
    return redirect(url_for('location.list_location'))


@bp.route('/api/admin1/<int:country_id>')
@login_required
def get_admin1_by_country(country_id):
    adm1_list = adm1_service.get_all(filters={"country_id": country_id, "enable": True})
    return jsonify([{"id": a.id, "name": a.name} for a in adm1_list])

@bp.route('/api/admin2/<int:admin1_id>')
@login_required
def get_admin2_by_admin1(admin1_id):
    adm2_list = adm2_service.get_all(filters={"admin_1_id": admin1_id, "enable": True})
    return jsonify([{"id": a.id, "name": a.name} for a in adm2_list])

@bp.route('/location/bulk_action', methods=['POST'])
@login_required
@require_module_access(Module.GEOGRAPHIC, permission_type='delete')
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    if not ids:
        flash('No se seleccionaron locaciones.', 'warning')
        return redirect(url_for('location.list_location'))

    count = 0
    for loc_id in ids:
        try:
            loc_id_int = int(loc_id)
            if action == 'disable':
                if location_service.delete(loc_id_int):
                    count += 1
            elif action == 'recover':
                location_service.update(id=loc_id_int, obj_in={"enable": True})
                count += 1
        except Exception:
            continue

    if action == 'disable':
        flash(f'{count} locación(es) deshabilitada(s).', 'warning')
    elif action == 'recover':
        flash(f'{count} locación(es) recuperada(s).', 'success')
    else:
        flash('Acción no reconocida.', 'danger')
    return redirect(url_for('location.list_location'))