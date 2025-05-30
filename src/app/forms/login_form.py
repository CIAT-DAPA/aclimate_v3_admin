from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Optional

class LoginForm(FlaskForm):
    email = StringField(_l('Email'), 
                       validators=[
                           Optional(),  # Permitimos validación en cliente
                           Email(message=_l('Ingresa un email válido'))
                       ], 
                       render_kw={"placeholder": "admin@test.com"})
    
    password = PasswordField(_l('Contraseña'), 
                           validators=[
                               Optional()  # Permitimos validación en cliente
                           ],
                           render_kw={"placeholder": _l("Ingresa tu contraseña")})
    
    submit = SubmitField(_l('Iniciar Sesión'))