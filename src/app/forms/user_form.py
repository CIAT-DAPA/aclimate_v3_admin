from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email

class UserForm(FlaskForm):
    username = StringField(
        _l('Nombre de Usuario'),
        validators=[
            DataRequired(message=_l('El nombre de usuario es obligatorio.')),
            Length(min=3, max=50, message=_l('El nombre de usuario debe tener entre 3 y 50 caracteres.'))
        ]
    )

    email = StringField(
        _l('Email'),
        validators=[
            DataRequired(message=_l('El email es obligatorio.')),
            Email(message=_l('Ingrese un email válido.')),
            Length(max=255, message=_l('Máximo 255 caracteres.'))
        ]
    )

    first_name = StringField(
        _l('Nombre'),
        validators=[
            DataRequired(message=_l('El nombre es obligatorio.')),
            Length(max=50, message=_l('Máximo 50 caracteres.'))
        ]
    )

    last_name = StringField(
        _l('Apellido'),
        validators=[
            DataRequired(message=_l('El apellido es obligatorio.')),
            Length(max=50, message=_l('Máximo 50 caracteres.'))
        ]
    )

    password = StringField(
        _l('Contraseña'),
        validators=[
            DataRequired(message=_l('La contraseña es obligatoria.'))
        ]
    )

    submit = SubmitField(_l('Guardar Usuario'))