from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import SelectField, FloatField, BooleanField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class PhenologicalStageStressForm(FlaskForm):
    stress_id = SelectField(
        _l('Estrés'),
        coerce=int,
        validators=[DataRequired(message=_l('Debe seleccionar un estrés.'))],
        choices=[]  # Llena dinámicamente en la vista
    )

    phenological_stage_id = SelectField(
        _l('Etapa fenológica'),
        coerce=int,
        validators=[DataRequired(message=_l('Debe seleccionar una etapa fenológica.'))],
        choices=[]  # Llena dinámicamente en la vista
    )

    max = FloatField(
        _l('Valor máximo'),
        validators=[
            DataRequired(message=_l('Debe ingresar el valor máximo.'))
        ]
    )

    min = FloatField(
        _l('Valor mínimo'),
        validators=[
            DataRequired(message=_l('Debe ingresar el valor mínimo.'))
        ]
    )

    enable = BooleanField(_l('¿Está habilitado?'), default=True)

    submit = SubmitField(_l('Guardar'))