from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Optional

class IndicatorForm(FlaskForm):
    name = StringField(
        _l('Nombre'),
        validators=[
            DataRequired(message=_l('El nombre es obligatorio.')),
            Length(max=150, message=_l('Máximo 150 caracteres.'))
        ]
    )

    short_name = StringField(
        _l('Nombre corto'),
        validators=[
            DataRequired(message=_l('El nombre corto es obligatorio.')),
            Length(max=50, message=_l('Máximo 50 caracteres.'))
        ]
    )

    unit = StringField(
        _l('Unidad'),
        validators=[
            DataRequired(message=_l('La unidad es obligatoria.')),
            Length(max=25, message=_l('Máximo 25 caracteres.'))
        ]
    )

    type = SelectField(
        _l('Tipo'),
        choices=[],  # Llena dinámicamente en la vista con [(valor, etiqueta), ...]
        validators=[DataRequired(message=_l('Debe seleccionar un tipo.'))]
    )

    indicator_category_id = SelectField(
        _l('Categoría'),
        choices=[],  # Llena dinámicamente en la vista con [(valor, etiqueta), ...]
        coerce=int,
        validators=[DataRequired(message=_l('Debe seleccionar una categoría.'))]
    )

    description = TextAreaField(
        _l('Descripción'),
        validators=[Optional()]
    )

    enable = BooleanField(_l('¿Está habilitado?'), default=True)

    submit = SubmitField(_l('Guardar'))