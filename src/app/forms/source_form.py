from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class SourceForm(FlaskForm):
    name = StringField(
        _l('Nombre'),
        validators=[
            DataRequired(message=_l('El nombre es obligatorio.')),
            Length(max=255, message=_l('Máximo 255 caracteres.'))
        ]
    )

    source_type = SelectField(
        _l('Tipo de fuente'),
        coerce=str,  # O usa el tipo adecuado según SourceType
        validators=[DataRequired(message=_l('Debe seleccionar un tipo de fuente.'))],
        choices=[]  # Llena dinámicamente en la vista
    )

    #enable = BooleanField(_l('¿Está habilitado?'), default=True)

    submit = SubmitField(_l('Guardar'))