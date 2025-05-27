from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], 
                       render_kw={"placeholder": "admin@test.com"})
    password = PasswordField('Contraseña', validators=[DataRequired()],
                           render_kw={"placeholder": "Ingresa tu contraseña"})
    submit = SubmitField('Iniciar Sesión')