from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp

class CountryForm(FlaskForm):
    name = StringField(
        _l('Nombre del país'),
        validators=[
            DataRequired(message=_l('El nombre es obligatorio.')),
            Length(max=255, message=_l('Máximo 255 caracteres.'))
        ]
    )

    iso2 = StringField(
        _l('Código ISO2'),
        validators=[
            DataRequired(message=_l('El código ISO2 es obligatorio.')),
            Length(min=2, max=2, message=_l('Debe tener exactamente 2 letras.')),
            Regexp(r'^[A-Z]{2}$', message=_l('Debe contener solo letras mayúsculas.'))
        ]
    )

    enable = BooleanField(_l('¿Está habilitado?'), default=True)

    submit = SubmitField(_l('Guardar'))