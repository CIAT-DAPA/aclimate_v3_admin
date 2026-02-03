from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import _
from aclimate_v3_orm.services import MngCountryIndicatorService, MngIndicatorsFeaturesService
from aclimate_v3_orm.schemas import IndicatorFeatureCreate, IndicatorFeatureUpdate
from aclimate_v3_orm.enums import IndicatorFeatureType
from app.forms.indicator_features_form import IndicatorFeaturesForm
from app.decorators.permissions import require_module_access
from app.config.permissions import Module

bp = Blueprint('indicator_features', __name__)
country_indicator_service = MngCountryIndicatorService()
indicator_features_service = MngIndicatorsFeaturesService()

@bp.route('/indicator_features', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.INDICATORS_DATA, permission_type='read')
def list_indicator_features():
    can_create = current_user.has_module_access(Module.INDICATORS_DATA.value, 'create')
    
    form = IndicatorFeaturesForm()
    # Obtener todas las relaciones país-indicador
    country_indicators = country_indicator_service.get_all()
    form.country_indicator_id.choices = [
        (ci.id, f"{ci.country.name} - {ci.indicator.name}")
        for ci in country_indicators
    ]
    form.type.choices = [(t.value, _(t.value.capitalize())) for t in IndicatorFeatureType]

    if form.validate_on_submit():
        if not can_create:
            flash(_('No tienes permiso para crear características de indicadores.'), 'danger')
            return redirect(url_for('indicator_features.list_indicator_features'))
        
        try:
            new_feature = IndicatorFeatureCreate(
                country_indicator_id=form.country_indicator_id.data,
                title=form.title.data,
                description=form.description.data if form.description.data else None,
                type=form.type.data
            )
            indicator_features_service.create(new_feature)
            flash(_('Característica de indicador agregada correctamente.'), 'success')
            return redirect(url_for('indicator_features.list_indicator_features'))
        except Exception as e:
            flash(_('Error al crear la característica: ') + str(e), 'danger')
            features_list = _get_features_with_relations()
            return render_template('indicator_features/list.html', 
                                 indicator_features=features_list, 
                                 form=form, 
                                 can_create=can_create)

    features_list = _get_features_with_relations()
    
    return render_template('indicator_features/list.html', 
                         indicator_features=features_list, 
                         form=form, 
                         can_create=can_create)

def _get_features_with_relations():
    """Helper function to get features with their country_indicator relations"""
    from aclimate_v3_orm.database import get_db
    from aclimate_v3_orm.models import MngIndicatorsFeatures, MngCountryIndicator, MngCountry, MngIndicator
    from sqlalchemy.orm import joinedload
    
    with get_db() as session:
        features = session.query(MngIndicatorsFeatures)\
            .options(joinedload(MngIndicatorsFeatures.country_indicator)
                    .joinedload(MngCountryIndicator.country))\
            .options(joinedload(MngIndicatorsFeatures.country_indicator)
                    .joinedload(MngCountryIndicator.indicator))\
            .all()
        
        # Detach objects from session to use them outside
        session.expunge_all()
        return features

@bp.route('/indicator_features/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.INDICATORS_DATA, permission_type='update')
def edit_indicator_features(id):
    # Get the feature with relations using ORM directly
    from aclimate_v3_orm.database import get_db
    from aclimate_v3_orm.models import MngIndicatorsFeatures, MngCountryIndicator, MngCountry, MngIndicator
    from sqlalchemy.orm import joinedload
    
    with get_db() as session:
        if_item = session.query(MngIndicatorsFeatures)\
            .options(joinedload(MngIndicatorsFeatures.country_indicator)
                    .joinedload(MngCountryIndicator.country))\
            .options(joinedload(MngIndicatorsFeatures.country_indicator)
                    .joinedload(MngCountryIndicator.indicator))\
            .filter(MngIndicatorsFeatures.id == id)\
            .first()
        
        if not if_item:
            flash(_('Registro no encontrado.'), 'danger')
            return redirect(url_for('indicator_features.list_indicator_features'))
        
        # Detach from session
        session.expunge_all()

    form = IndicatorFeaturesForm(obj=if_item)
    country_indicators = country_indicator_service.get_all()
    form.country_indicator_id.choices = [
        (ci.id, f"{ci.country.name} - {ci.indicator.name}")
        for ci in country_indicators
    ]
    form.type.choices = [(t.value, _(t.value.capitalize())) for t in IndicatorFeatureType]

    if request.method == 'GET':
        form.country_indicator_id.data = if_item.country_indicator_id
        form.title.data = if_item.title
        form.description.data = if_item.description
        form.type.data = if_item.type

    if form.validate_on_submit():
        try:
            update_data = IndicatorFeatureUpdate(
                title=form.title.data,
                description=form.description.data if form.description.data else None,
                type=form.type.data
            )
            indicator_features_service.update(id=id, obj_in=update_data)
            flash(_('Característica de indicador actualizada.'), 'success')
            return redirect(url_for('indicator_features.list_indicator_features'))
        except Exception as e:
            flash(_('Error al actualizar: ') + str(e), 'danger')
            return render_template('indicator_features/edit.html', form=form, indicator_feature=if_item)
    
    return render_template('indicator_features/edit.html', form=form, indicator_feature=if_item)

@bp.route('/indicator_features/delete/<int:id>')
@login_required
@require_module_access(Module.INDICATORS_DATA, permission_type='delete')
def delete_indicator_features(id):
    if not indicator_features_service.delete(id):
        flash(_('No se pudo eliminar.'), 'danger')
    else:
        flash(_('Característica de indicador eliminada.'), 'warning')
    return redirect(url_for('indicator_features.list_indicator_features'))

@bp.route('/indicator_features/bulk_action', methods=['POST'])
@login_required
@require_module_access(Module.INDICATORS_DATA, permission_type='delete')
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    
    if not ids:
        flash(_('No se seleccionaron características.'), 'warning')
        return redirect(url_for('indicator_features.list_indicator_features'))

    count = 0
    for feature_id in ids:
        try:
            feature_id_int = int(feature_id)
            if action == 'disable':
                if indicator_features_service.delete(feature_id_int):
                    count += 1
        except Exception:
            continue

    if action == 'disable':
        flash(f'{count} característica(s) eliminada(s).', 'warning')
    else:
        flash('Acción no reconocida.', 'danger')
    
    return redirect(url_for('indicator_features.list_indicator_features'))
