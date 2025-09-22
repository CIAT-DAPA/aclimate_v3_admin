from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Optional

class StressForm(FlaskForm):
    name = StringField(
        _l('Nombre'),
        validators=[
            DataRequired(message=_l('El nombre es obligatorio.')),
            Length(max=255, message=_l('Máximo 255 caracteres.'))
        ]
    )

    short_name = StringField(
        _l('Nombre corto'),
        validators=[
            DataRequired(message=_l('El nombre corto es obligatorio.')),
            Length(max=100, message=_l('Máximo 100 caracteres.'))
        ]
    )

    category = SelectField(
        _l('Categoría'),
        choices=[],  # Llena dinámicamente en la vista con [(valor, etiqueta), ...]
        validators=[DataRequired(message=_l('Debe seleccionar una categoría.'))]
    )

    description = TextAreaField(
        _l('Descripción'),
        validators=[Optional()]
    )

    enable = BooleanField(_l('¿Está habilitado?'), default=True)

    submit = SubmitField(_l('Guardar'))