from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import _
from aclimate_v3_orm.services import MngIndicatorCategoryService
from aclimate_v3_orm.schemas import IndicatorCategoryCreate, IndicatorCategoryUpdate
from app.forms.indicator_category_form import IndicatorCategoryForm
from app.decorators.permissions import require_module_access
from app.config.permissions import Module

bp = Blueprint('indicator_category', __name__)
category_service = MngIndicatorCategoryService()

@bp.route('/indicator_category', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.INDICATORS_DATA, permission_type='read')
def list_indicator_category():
    can_create = current_user.has_module_access(Module.INDICATORS_DATA.value, 'create')
    
    form = IndicatorCategoryForm()
    if form.validate_on_submit():
        if not can_create:
            flash(_('No tienes permiso para crear categorías.'), 'danger')
            return redirect(url_for('indicator_category.list_indicator_category'))
            
        new_category = IndicatorCategoryCreate(
            name=form.name.data,
            description=form.description.data,
            enable=True
        )
        category_service.create(new_category)
        flash(_('Categoría agregada correctamente.'), 'success')
        return redirect(url_for('indicator_category.list_indicator_category'))

    category_list = category_service.get_all()
    return render_template('indicator_category/list.html', categories=category_list, form=form, can_create=can_create)

@bp.route('/indicator_category/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.INDICATORS_DATA, permission_type='update')
def edit_indicator_category(id):
    category = category_service.get_by_id(id)
    if not category:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('indicator_category.list_indicator_category'))

    form = IndicatorCategoryForm(obj=category)
    if form.validate_on_submit():
        update_data = IndicatorCategoryUpdate(
            name=form.name.data,
            description=form.description.data,
            enable=form.enable.data
        )
        category_service.update(id=id, obj_in=update_data)
        flash(_('Categoría actualizada.'), 'success')
        return redirect(url_for('indicator_category.list_indicator_category'))

    return render_template('indicator_category/edit.html', form=form, category=category)

@bp.route('/indicator_category/delete/<int:id>')
@login_required
@require_module_access(Module.INDICATORS_DATA, permission_type='delete')
def delete_indicator_category(id):
    if not category_service.delete(id):
        flash(_('No se pudo deshabilitar.'), 'danger')
    else:
        flash(_('Categoría deshabilitada.'), 'warning')
    return redirect(url_for('indicator_category.list_indicator_category'))

@bp.route('/indicator_category/reset/<int:id>')
@login_required
@require_module_access(Module.INDICATORS_DATA, permission_type='update')
def reset_indicator_category(id):
    category = category_service.get_by_id(id)
    if not category:
        flash(_('Registro no encontrado.'), 'danger')
        return redirect(url_for('indicator_category.list_indicator_category'))

    category_service.update(id=id, obj_in={"enable": True})
    flash(_('Categoría reactivada.'), 'success')
    return redirect(url_for('indicator_category.list_indicator_category'))

@bp.route('/indicator_category/bulk_action', methods=['POST'])
@login_required
@require_module_access(Module.INDICATORS_DATA, permission_type='delete')
def bulk_action():
    ids = request.form.getlist('selected_ids')
    action = request.form.get('action')
    if not ids:
        flash('No se seleccionaron categorías.', 'warning')
        return redirect(url_for('indicator_category.list_indicator_category'))

    count = 0
    for category_id in ids:
        try:
            category_id_int = int(category_id)
            if action == 'disable':
                if category_service.delete(category_id_int):
                    count += 1
            elif action == 'recover':
                category_service.update(id=category_id_int, obj_in={"enable": True})
                count += 1
        except Exception:
            continue

    if action == 'disable':
        flash(f'{count} categoría(s) deshabilitada(s).', 'warning')
    elif action == 'recover':
        flash(f'{count} categoría(s) recuperada(s).', 'success')
    else:
        flash('Acción no reconocida.', 'danger')
    return redirect(url_for('indicator_category.list_indicator_category'))