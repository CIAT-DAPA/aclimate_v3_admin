from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Optional

class PhenologicalStageForm(FlaskForm):

    crop = SelectField(
        _l('Cultivo'),
        coerce=int,
        validators=[DataRequired(message=_l('Debe seleccionar un cultivo.'))],
        choices=[]  # Llena dinámicamente en la vista con [(valor, etiqueta), ...]
    )

    name = StringField(
        _l('Nombre'),
        validators=[
            DataRequired(message=_l('El nombre es obligatorio.')),
            Length(max=255, message=_l('Máximo 255 caracteres.'))
        ]
    )

    short_name = StringField(
        _l('Nombre corto'),
        validators=[
            DataRequired(message=_l('El nombre corto es obligatorio.')),
            Length(max=100, message=_l('Máximo 100 caracteres.'))
        ]
    )

    description = TextAreaField(
        _l('Descripción'),
        validators=[Optional()]
    )

    order_stage = IntegerField(
        _l('Orden de aparición en la secuencia fenológica'),
        validators=[DataRequired(message=_l('Debe ingresar un orden de aparición.'))]
    )

    duration_avg_day = IntegerField(
        _l('Duración promedio en días de la fase)'),
        validators=[DataRequired(message=_l('Debe ingresar una duración promedio.'))]
    )

    enable = BooleanField(_l('¿Está habilitado?'), default=True)

    submit = SubmitField(_l('Guardar'))