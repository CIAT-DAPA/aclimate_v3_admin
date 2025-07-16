from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import SelectField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class SetupForm(FlaskForm):
    cultivar_id = SelectField(
        _l('Cultivar'),
        coerce=int,
        validators=[DataRequired(message=_l('Debe seleccionar un cultivar.') )],
        choices=[]  # Llena dinámicamente en la vista
    )

    soil_id = SelectField(
        _l('Suelo'),
        coerce=int,
        validators=[DataRequired(message=_l('Debe seleccionar un suelo.') )],
        choices=[]  # Llena dinámicamente en la vista
    )

    season_id = SelectField(
        _l('Temporada'),
        coerce=int,
        validators=[DataRequired(message=_l('Debe seleccionar una temporada.') )],
        choices=[]  # Llena dinámicamente en la vista
    )

    frequency = IntegerField(
        _l('Frecuencia'),
        validators=[
            DataRequired(message=_l('Debe ingresar la frecuencia.')),
            NumberRange(min=1, message=_l('La frecuencia debe ser mayor a 0.'))
        ]
    )

    enable = BooleanField(_l('¿Está habilitado?'), default=True)

    submit = SubmitField(_l('Guardar'))