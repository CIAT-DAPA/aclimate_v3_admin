from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

class IndicatorCategoryForm(FlaskForm):
    name = StringField(
        _l('Nombre'),
        validators=[
            DataRequired(message=_l('El nombre es obligatorio.')),
            Length(max=100, message=_l('Máximo 100 caracteres.'))
        ]
    )

    description = TextAreaField(
        _l('Descripción'),
        validators=[Optional()]
    )

    enable = BooleanField(_l('¿Está habilitado?'), default=True)

    submit = SubmitField(_l('Guardar'))