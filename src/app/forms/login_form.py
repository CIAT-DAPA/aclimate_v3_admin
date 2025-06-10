from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class LoginForm(FlaskForm):
    username = StringField(_l('Usuario'), 
                          validators=[
                              Optional(),  # Permitimos validación en cliente
                              Length(min=3, max=50, message=_l('El usuario debe tener entre 3 y 50 caracteres'))
                          ], 
                          render_kw={"placeholder": _l("Ingresa tu usuario")})
    
    password = PasswordField(_l('Contraseña'), 
                           validators=[
                               Optional()  # Permitimos validación en cliente
                           ],
                           render_kw={"placeholder": _l("Ingresa tu contraseña")})
    
    submit = SubmitField(_l('Iniciar Sesión'))