from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Optional

class LoginForm(FlaskForm):
    email = StringField('Email', 
                       validators=[
                           Optional(),  # Permitimos validación en cliente
                           Email(message='Ingresa un email válido')
                       ], 
                       render_kw={"placeholder": "admin@test.com"})
    
    password = PasswordField('Contraseña', 
                           validators=[
                               Optional()  # Permitimos validación en cliente
                           ],
                           render_kw={"placeholder": "Ingresa tu contraseña"})
    
    submit = SubmitField('Iniciar Sesión')