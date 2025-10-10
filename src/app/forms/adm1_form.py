from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class Adm1Form(FlaskForm):
    name = StringField(
        _l('Nombre'),
        validators=[
            DataRequired(message=_l('El nombre es obligatorio.')),
            Length(max=255, message=_l('Máximo 255 caracteres.'))
        ]
    )

    ext_id = StringField(
        _l('ID Externo'),
        validators=[
            Optional(),
            Length(max=255, message=_l('Máximo 255 caracteres.'))
        ],
        description=_l('Para Colombia: Código Divipola DANE del departamento')
    )

    country_id = SelectField(
        _l('País'),
        coerce=int,
        validators=[DataRequired(message=_l('Debe seleccionar un país.'))],
        choices=[]  
    )

    enable = BooleanField(_l('¿Está habilitado?'), default=True)

    submit = SubmitField(_l('Guardar'))