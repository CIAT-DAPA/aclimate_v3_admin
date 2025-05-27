from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp

class CountryForm(FlaskForm):
    name = StringField(
        'Nombre del país',
        validators=[
            DataRequired(message='El nombre es obligatorio.'),
            Length(max=255, message='Máximo 255 caracteres.')
        ]
    )

    iso2 = StringField(
        'Código ISO2',
        validators=[
            DataRequired(message='El código ISO2 es obligatorio.'),
            Length(min=2, max=2, message='Debe tener exactamente 2 letras.'),
            Regexp(r'^[A-Z]{2}$', message='Debe contener solo letras mayúsculas.')
        ]
    )

    enable = BooleanField('¿Está habilitado?', default=True)

    submit = SubmitField('Guardar')