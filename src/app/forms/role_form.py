from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, TextAreaField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Length
from app.config.permissions import Module, RolePermissionMapper

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
    
    description = TextAreaField(_l('Descripción'),
                               validators=[
                                   Length(max=255, message=_l('La descripción no puede exceder 255 caracteres'))
                               ],
                               render_kw={
                                   "placeholder": _l("Describe las responsabilidades de este rol..."),
                                   "rows": 3
                               })
    
    modules = MultiCheckboxField(_l('Módulos de Acceso'),
                                validators=[
                                    DataRequired(message=_l('Debe seleccionar al menos un módulo'))
                                ],
                                choices=[],  # Se llenará dinámicamente
                                coerce=str)
    
    def __init__(self, *args, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)
        # Llenar choices de módulos dinámicamente
        modules_info = RolePermissionMapper.get_modules_info()
        self.modules.choices = [
            (module_value, f"{info['name']} - {info['description']}")
            for module_value, info in modules_info.items()
        ]
    
class RoleEditForm(RoleForm):
    """Formulario para editar roles existentes"""
    pass