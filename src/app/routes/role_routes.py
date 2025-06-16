from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.forms.role_form import RoleForm
from app.services.role_service import RoleService
from app.decorators import token_required

bp = Blueprint('role', __name__)
role_service = RoleService()

# Ruta: Lista de roles
@bp.route('/role', methods=['GET'])
@token_required
def list_role():
    form = RoleForm()
    roles = role_service.get_all()
    return render_template('role/list.html', roles=roles, form=form)