from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import SelectField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class IndicatorFeaturesForm(FlaskForm):
    country_indicator_id = SelectField(
        _l('Relación País-Indicador'),
        choices=[],
        coerce=int,
        validators=[DataRequired(message=_l('La relación país-indicador es obligatoria.'))]
    )

    title = StringField(
        _l('Título'),
        validators=[
            DataRequired(message=_l('El título es obligatorio.')),
            Length(max=150, message=_l('El título no puede exceder 150 caracteres.'))
        ]
    )

    description = TextAreaField(
        _l('Descripción'),
        validators=[Optional()]
    )

    type = SelectField(
        _l('Tipo'),
        choices=[],
        validators=[DataRequired(message=_l('El tipo es obligatorio.'))]
    )

    submit = SubmitField(_l('Guardar'))
