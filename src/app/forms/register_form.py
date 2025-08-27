from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class RegisterForm(FlaskForm):
    username = StringField(_l('Usuario'), 
                          validators=[
                              Optional(),  # Permitimos validación en cliente
                              Length(min=3, max=50, message=_l('El usuario debe tener entre 3 y 50 caracteres'))
                          ], 
                          render_kw={"placeholder": _l("Ingresa tu usuario")})
    
    email = StringField(_l('Correo Electrónico'),
                        validators=[
                            Optional(),  # Permitimos validación en cliente
                            Length(min=5, max=100, message=_l('El correo electrónico debe tener entre 5 y 100 caracteres'))
                        ],
                        render_kw={"placeholder": _l("Ingresa tu correo electrónico")})
    
    name = StringField(_l('Nombre'),
                        validators=[
                            Optional(),  # Permitimos validación en cliente
                            Length(min=2, max=50, message=_l('El nombre debe tener entre 2 y 50 caracteres'))
                        ],
                        render_kw={"placeholder": _l("Ingresa tu nombre")})
    
    last_name = StringField(_l('Apellido'),
                            validators=[
                                 Optional(),  # Permitimos validación en cliente
                                 Length(min=2, max=50, message=_l('El apellido debe tener entre 2 y 50 caracteres'))
                            ],
                            render_kw={"placeholder": _l("Ingresa tu apellido")})
    
    password = PasswordField(_l('Contraseña'), 
                           validators=[
                               Optional()  # Permitimos validación en cliente
                           ],
                           render_kw={"placeholder": _l("Ingresa tu contraseña")})
    
    submit = SubmitField(_l('Crear Cuenta'))