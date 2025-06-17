from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length

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
    
    