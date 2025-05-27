from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class Adm2Form(FlaskForm):
    name = StringField(
        'Nombre',
        validators=[
            DataRequired(message='El nombre es obligatorio.'),
            Length(max=255, message='Máximo 255 caracteres.')
        ]
    )

    admin_1_id = SelectField(
        'División Adm1 asociada',
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar una división de nivel 1.')],
        choices=[] 
    )

    visible = BooleanField('¿Es visible?', default=True)
    enable = BooleanField('¿Está habilitado?', default=True)

    submit = SubmitField('Guardar')
