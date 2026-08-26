from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import SelectField, BooleanField, SubmitField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Optional
from wtforms.widgets import ListWidget, CheckboxInput


class MultiCheckboxField(SelectMultipleField):
    """Campo personalizado para múltiples checkboxes"""
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class CountryClimateMeasureForm(FlaskForm):
    country_id = SelectField(
        _l('País'),
        choices=[],
        validators=[DataRequired(message=_l('El país es obligatorio.'))]
    )

    measure_id = SelectField(
        _l('Variable climática'),
        choices=[],
        coerce=int,
        validators=[DataRequired(message=_l('La variable climática es obligatoria.'))]
    )

    spatial_forecast = BooleanField(_l('Pronóstico espacial'), default=False)
    spatial_climate = BooleanField(_l('Clima espacial'), default=False)
    location_forecast = BooleanField(_l('Pronóstico por ubicación'), default=False)
    location_climate = BooleanField(_l('Clima por ubicación'), default=False)

    location_climate_conf = MultiCheckboxField(
        _l('Temporalidades clima por ubicación'),
        choices=[],  # Llena dinámicamente en la vista con [(valor, etiqueta), ...]
        coerce=str,
        default=list
    )

    description = TextAreaField(
        _l('Descripción'),
        validators=[Optional()]
    )

    submit = SubmitField(_l('Guardar'))