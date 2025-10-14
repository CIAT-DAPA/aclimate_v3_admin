from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class Adm2Form(FlaskForm):
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
        description=_l('Para Colombia: Código Divipola DANE del municipio')
    )

    admin_1_id = SelectField(
        _l('División Adm1 asociada'),
        coerce=int,
        validators=[DataRequired(message=_l('Debe seleccionar una división de nivel 1.'))],
        choices=[] 
    )

    visible = BooleanField(_l('¿Es visible?'), default=True)
    enable = BooleanField(_l('¿Está habilitado?'), default=True)

    submit = SubmitField(_l('Guardar'))
