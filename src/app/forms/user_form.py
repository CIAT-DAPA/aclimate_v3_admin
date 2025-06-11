from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, SelectField, SelectMultipleField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from wtforms.widgets import CheckboxInput, ListWidget

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

    # Para un solo rol (actual)
    role_id = SelectField(
        _l('Rol'),
        coerce=int,
        validators=[DataRequired(message=_l('Debe seleccionar un rol.'))],
        choices=[]
    )

    # Para múltiples roles (futuro)
    roles = SelectMultipleField(
        _l('Roles Adicionales'),
        coerce=int,
        choices=[],
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput()
    )

    enable = BooleanField(_l('¿Está habilitado?'), default=True)

    submit = SubmitField(_l('Guardar Usuario'))