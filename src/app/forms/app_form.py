from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class AppForm(FlaskForm):
    name = StringField(
        _l('Nombre'),
        validators=[
            DataRequired(message=_l('El nombre es obligatorio.')),
            Length(max=255, message=_l('Máximo 255 caracteres.'))
        ]
    )

    country_ext_id = StringField(
        _l('ID externo del país'),
        validators=[
            DataRequired(message=_l('El ID externo del país es obligatorio.')),
            Length(max=50, message=_l('Máximo 50 caracteres.'))
        ]
    )

    enable = BooleanField(_l('¿Está habilitado?'), default=True)

    submit = SubmitField(_l('Guardar'))
