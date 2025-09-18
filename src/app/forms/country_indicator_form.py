from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import SelectField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional
import json
from wtforms import ValidationError

def validate_json(form, field):
    if field.data:
        try:
            json.loads(field.data)
        except Exception:
            raise ValidationError(_l('Debe ser un JSON válido.'))

class CountryIndicatorForm(FlaskForm):
    country_id = SelectField(
        _l('País'),
        choices=[],  
        validators=[DataRequired(message=_l('El país es obligatorio.'))]
    )

    indicator_id = SelectField(
        _l('Indicador'),
        choices=[], 
        coerce=int,
        validators=[DataRequired(message=_l('El indicador es obligatorio.'))]
    )

    spatial_forecast = BooleanField(_l('Pronóstico espacial'), default=False)
    spatial_climate = BooleanField(_l('Clima espacial'), default=False)
    location_forecast = BooleanField(_l('Pronóstico por ubicación'), default=False)
    location_climate = BooleanField(_l('Clima por ubicación'), default=False)

    criteria = TextAreaField(
        _l('Criterios (JSON)'),
        validators=[Optional(), validate_json]
    )

    submit = SubmitField(_l('Guardar'))