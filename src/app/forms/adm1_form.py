from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class Adm1Form(FlaskForm):
    name = StringField(
        'Nombre',
        validators=[
            DataRequired(message='El nombre es obligatorio.'),
            Length(max=255, message='Máximo 255 caracteres.')
        ]
    )

    country_id = SelectField(
        'País',
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar un país.')],
        choices=[]  
    )

    enable = BooleanField('¿Está habilitado?', default=True)

    submit = SubmitField('Guardar')