from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, TextAreaField, SelectMultipleField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import CheckboxInput, ListWidget

class MultiCheckboxField(SelectMultipleField):
    """Campo para múltiples checkboxes"""
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

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
    
    modules = MultiCheckboxField(
        _l('Módulos de Acceso'),
        choices=[
            ('geographic', _l('Geográfico - Gestión de información geográfica')),
            ('crops', _l('Cultivos - Administración de cultivos')),
            ('weather', _l('Clima - Información meteorológica')),
            ('users', _l('Usuarios - Gestión de usuarios del sistema')),
            ('api', _l('API - Acceso a interfaces de programación'))
        ],
        validators=[DataRequired(message=_l('Debe seleccionar al menos un módulo'))]
    )
    
    enable = BooleanField(_l('Habilitado'), default=True)
    
    submit = SubmitField(_l('Guardar Rol'))
    
    def __init__(self, *args, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)
        # Puedes personalizar las opciones de módulos dinámicamente aquí si es necesario
        # Por ejemplo, obtener módulos desde una configuración o servicio
    
    def populate_modules_from_service(self, role_service):
        """Método para poblar dinámicamente los módulos desde el servicio"""
        available_modules = role_service.get_available_modules()
        
        # Mapeo de nombres técnicos a nombres amigables
        module_labels = {
            'geographic': 'Geográfico - Gestión de información geográfica',
            'crops': 'Cultivos - Administración de cultivos y plantaciones',
            'weather': 'Clima - Información y pronósticos meteorológicos',
            'users': 'Usuarios - Gestión de usuarios del sistema',
            'api': 'API - Acceso a interfaces de programación'
        }
        
        choices = []
        for module in available_modules:
            label = module_labels.get(module, module.title())
            choices.append((module, label))
        
        self.modules.choices = choices
    
    def set_module_data_from_role(self, role_data):
        """Método para establecer los módulos activos desde datos de rol"""
        if 'modules' in role_data:
            active_modules = []
            for module, access in role_data['modules'].items():
                if access:
                    active_modules.append(module)
            self.modules.data = active_modules
    
    def get_modules_dict(self):
        """Convierte la selección de módulos a diccionario"""
        modules_dict = {
            'geographic': False,
            'crops': False,
            'weather': False,
            'users': False,
            'api': False
        }
        
        if self.modules.data:
            for module in self.modules.data:
                if module in modules_dict:
                    modules_dict[module] = True
        
        return modules_dict