from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_babel import lazy_gettext as _l
from wtforms import SubmitField, SelectField
from wtforms.validators import DataRequired

class LocationImportForm(FlaskForm):
    country_id = SelectField(
        _l('País'),
        coerce=int,
        validators=[DataRequired()],
        description=_l('Selecciona el país al que pertenecen las locaciones')
    )
    
    csv_file = FileField(
        _l('Archivo CSV'),
        validators=[
            FileRequired(message=_l('Debe seleccionar un archivo.')),
            FileAllowed(['csv'], message=_l('Solo se permiten archivos CSV.'))
        ],
        description=_l('Formato: ext_id, name, latitude, longitude, altitude, admin_level_1, ext_id_level_1, admin_level_2, ext_id_level_2, source_name, type_of_source')
    )
    
    submit = SubmitField(_l('Importar Locaciones'))
