from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, Optional
from wtforms.widgets import CheckboxInput, ListWidget

class MultiCheckboxField(SelectMultipleField):
    """Campo personalizado para múltiples checkboxes"""
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

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

    countries = MultiCheckboxField(
        _l('Países'),
        validators=[
            Optional()
        ],
        choices=[],
        coerce=str,
        description=_l('Seleccione los países a los que el usuario tendrá acceso.')
    )

    submit = SubmitField(_l('Guardar Usuario'))

    def populate_countries(self, available_countries):
        """Poblar las opciones de países disponibles"""
        # Crear choices con formato (valor, etiqueta)
        self.countries.choices = [
            (country['name'], country['display_name']) 
            for country in available_countries
        ]

class UserEditForm(FlaskForm):
    """Formulario para editar usuario"""
    first_name = StringField(
        _l('Nombre'),
        validators=[
            Optional(),
            Length(max=50, message=_l('Máximo 50 caracteres.'))
        ]
    )

    last_name = StringField(
        _l('Apellido'),
        validators=[
            Optional(),
            Length(max=50, message=_l('Máximo 50 caracteres.'))
        ]
    )

    email = StringField(
        _l('Email'),
        validators=[
            Optional(),
            Email(message=_l('Ingrese un email válido.')),
            Length(max=255, message=_l('Máximo 255 caracteres.'))
        ]
    )

    role_id = SelectField(
        _l('Rol'),
        validators=[
            DataRequired(message=_l('Debe seleccionar un rol.'))
        ],
        choices=[],  # Se llenarán dinámicamente
        coerce=str
    )

    countries = MultiCheckboxField(
        _l('Países'),
        validators=[
            Optional()
        ],
        choices=[],  # Se llenarán dinámicamente con países disponibles
        coerce=str,
        description=_l('Seleccione los países a los que el usuario tendrá acceso.')
    )

    submit = SubmitField(_l('Actualizar Usuario'))

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        # Las opciones se establecerán desde la vista
        
    def populate_countries(self, available_countries, user_countries=None):
        """Poblar las opciones de países disponibles"""
        # Crear choices con formato (valor, etiqueta)
        self.countries.choices = [
            (country['name'], country['display_name']) 
            for country in available_countries
        ]
        
        # Si se proporcionan países del usuario, pre-seleccionarlos
        if user_countries:
            if isinstance(user_countries, list) and len(user_countries) > 0:
                if isinstance(user_countries[0], dict):
                    # Si user_countries es una lista de diccionarios
                    self.countries.data = [country['name'] for country in user_countries]
                else:
                    # Si user_countries es una lista de strings
                    self.countries.data = user_countries
    
    def populate_roles(self, available_roles, user_role=None):
        """Poblar las opciones de roles disponibles"""
        # Crear choices con formato (valor, etiqueta)
        self.role_id.choices = [
            (role['id'], role['display_name']) 
            for role in available_roles
        ]
        
        # Si se proporciona rol del usuario, pre-seleccionarlo
        if user_role:
            self.role_id.data = user_role

    def validate_countries(self, field):
        """Validación personalizada para países"""
        # Permitir que no se seleccionen países (opcional)
        # Si necesitas hacer obligatorio al menos un país, puedes agregar validación aquí
        pass