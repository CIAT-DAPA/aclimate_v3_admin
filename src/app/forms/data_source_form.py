from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, BooleanField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
import json

def json_validator(form, field):
    if field.data:
        try:
            json.loads(field.data)
        except Exception:
            raise ValidationError(_l('El contenido debe estar en formato JSON válido.'))

class DataSourceForm(FlaskForm):
    country_id = SelectField(
        _l('País'),
        coerce=int,
        validators=[DataRequired(message=_l('Debe seleccionar un país.'))],
        choices=[]  # Llena dinámicamente en la vista
    )

    name = StringField(
        _l('Nombre'),
        validators=[
            DataRequired(message=_l('El nombre es obligatorio.')),
            Length(max=255, message=_l('Máximo 255 caracteres.'))
        ]
    )

    description = TextAreaField(
        _l('Descripción'),
        validators=[Optional(), Length(max=1000, message=_l('Máximo 1000 caracteres.'))]
    )

    type = StringField(
        _l('Tipo de fuente'),
        validators=[
            DataRequired(message=_l('El tipo de fuente es obligatorio.')),
            Length(max=100, message=_l('Máximo 100 caracteres.'))
        ]
    )

    #enable = BooleanField(_l('¿Está habilitado?'), default=True)

    template = SelectField(
        _l('Plantilla JSON'),
        choices=[
            ('', _l('Seleccionar plantilla...')),
            ('sst_iridl', _l('SST - IRIDL')),
            ('copernicus', _l('Copernicus')),
            ('chirps', _l('CHIRPS - Precipitación')),
            ('era5_single', _l('ERA5 - Temperatura Máxima')),
            ('era5_full', _l('ERA5 - Todas las variables')),
            ('climatology', _l('Generación de Climatología')),
            ('full_workflow', _l('Flujo completo CHIRPS+ERA5')),
            ('custom', _l('Personalizado'))
        ],
        default='',
        render_kw={"onchange": "loadTemplate(this)"}
    )

    content = TextAreaField(
        _l('Contenido en formato JSON'),
        validators=[Optional(), json_validator]
    )

    submit = SubmitField(_l('Guardar'))