from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class ClimateMeasureForm(FlaskForm):
    name = StringField(
        _l('Nombre'),
        validators=[
            DataRequired(message=_l('El nombre es obligatorio.')),
            Length(max=150, message=_l('Máximo 150 caracteres.'))
        ]
    )

    short_name = StringField(
        _l('Nombre corto'),
        validators=[
            DataRequired(message=_l('El nombre corto es obligatorio.')),
            Length(max=75, message=_l('Máximo 75 caracteres.'))
        ]
    )

    unit = StringField(
        _l('Unidad'),
        validators=[
            DataRequired(message=_l('La unidad es obligatoria.')),
            Length(max=50, message=_l('Máximo 50 caracteres.'))
        ]
    )

    description = TextAreaField(
        _l('Descripción'),
        validators=[Optional()]
    )

    enable = BooleanField(_l('¿Está habilitado?'), default=True)

    submit = SubmitField(_l('Guardar'))
