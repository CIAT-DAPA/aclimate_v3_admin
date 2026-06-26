from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import SelectField, BooleanField, SubmitField, TextAreaField, StringField
from wtforms.validators import DataRequired, Optional


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

    description = TextAreaField(
        _l('Descripción'),
        validators=[Optional()]
    )

    store = StringField(
        _l('Store'),
        validators=[Optional()]
    )

    workspace = StringField(
        _l('Workspace'),
        validators=[Optional()]
    )

    submit = SubmitField(_l('Guardar'))