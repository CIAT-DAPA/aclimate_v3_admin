from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, BooleanField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange

class SoilForm(FlaskForm):
    country_id = SelectField(
        _l('País'),
        coerce=int,
        validators=[DataRequired(message=_l('Debe seleccionar un país.'))],
        choices=[]  # Llena dinámicamente en la vista
    )

    crop_id = SelectField(
        _l('Cultivo'),
        coerce=int,
        validators=[DataRequired(message=_l('Debe seleccionar un cultivo.'))],
        choices=[]  # Llena dinámicamente en la vista
    )

    name = StringField(
        _l('Nombre'),
        validators=[
            DataRequired(message=_l('El nombre es obligatorio.')),
            Length(max=255, message=_l('Máximo 255 caracteres.'))
        ]
    )

    sort_order = IntegerField(
        _l('Orden'),
        validators=[
            DataRequired(message=_l('Debe ingresar el orden.')),
            NumberRange(min=1, message=_l('El orden debe ser mayor a 0.'))
        ]
    )

    enable = BooleanField(_l('¿Está habilitado?'), default=True)

    submit = SubmitField(_l('Guardar'))