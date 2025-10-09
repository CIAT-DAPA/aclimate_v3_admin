from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, TextAreaField, SelectMultipleField, widgets, SubmitField
from wtforms.validators import DataRequired, Length
from app.config.permissions import get_modules_info

class MultiCheckboxField(SelectMultipleField):
    """Campo personalizado para múltiples checkboxes"""
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class RoleForm(FlaskForm):
    name = StringField(_l('Nombre del Rol'), 
                      validators=[
                          DataRequired(message=_l('El nombre del rol es requerido')),
                          Length(min=2, max=50, message=_l('El nombre debe tener entre 2 y 50 caracteres'))
                      ],
                      render_kw={"placeholder": _l("Ej: Editor, Administrador, Visualizador")})
    
    # NOTA: 'description' y 'modules' eliminados del formulario
    # Los permisos ahora se manejan en user_access (por usuario, país y módulo)
    # No se asignan módulos directamente a roles
    
    def __init__(self, *args, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)
    
class RoleEditForm(FlaskForm):
    """Formulario para editar roles existentes - solo módulos"""
    
    modules = SelectMultipleField(_l('Módulos de Acceso'),
                                 validators=[
                                     DataRequired(message=_l('Debe seleccionar al menos un módulo'))
                                 ],
                                 choices=[],  # Se llenará dinámicamente
                                 coerce=str,
                                 render_kw={"class": "form-control"})
    
    submit = SubmitField(_l('Guardar Cambios'))
    
    def __init__(self, *args, **kwargs):
        super(RoleEditForm, self).__init__(*args, **kwargs)
        # Llenar choices de módulos dinámicamente con información descriptiva
        modules_info = get_modules_info()
        self.modules.choices = [
            (module_value, f"{info['name']} - {info['description']}")
            for module_value, info in modules_info.items()
        ]