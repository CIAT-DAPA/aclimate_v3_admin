from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import SelectField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired

class SeasonForm(FlaskForm):
    location_id = SelectField(
        _l('Localidad'),
        coerce=int,
        validators=[DataRequired(message=_l('Debe seleccionar una localidad.'))],
        choices=[]  # Llena dinámicamente en la vista
    )

    crop_id = SelectField(
        _l('Cultivo'),
        coerce=int,
        validators=[DataRequired(message=_l('Debe seleccionar un cultivo.'))],
        choices=[]  # Llena dinámicamente en la vista
    )

    planting_start = DateField(
        _l('Inicio de siembra'),
        format='%Y-%m-%d',
        validators=[DataRequired(message=_l('Debe ingresar la fecha de inicio de siembra.'))]
    )

    planting_end = DateField(
        _l('Fin de siembra'),
        format='%Y-%m-%d',
        validators=[DataRequired(message=_l('Debe ingresar la fecha de fin de siembra.'))]
    )

    season_start = DateField(
        _l('Inicio de temporada'),
        format='%Y-%m-%d',
        validators=[DataRequired(message=_l('Debe ingresar la fecha de inicio de temporada.'))]
    )

    season_end = DateField(
        _l('Fin de temporada'),
        format='%Y-%m-%d',
        validators=[DataRequired(message=_l('Debe ingresar la fecha de fin de temporada.'))]
    )

    enable = BooleanField(_l('¿Está habilitado?'), default=True)

    submit = SubmitField(_l('Guardar'))