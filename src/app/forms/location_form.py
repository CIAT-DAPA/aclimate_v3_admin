from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, BooleanField, SelectField, SubmitField, FloatField
from wtforms.validators import DataRequired, Length, NumberRange

class LocationForm(FlaskForm):
    country = SelectField(
        _l('País'),
        validators=[
            DataRequired(message=_l('Debe seleccionar un país.'))
        ],
        choices=[('', '---------')] 
    )

    source_id = SelectField(
        _l('Id del origen'),
        validators=[
            DataRequired(message=_l('Seleccione un id origen.'))
        ],
        choices=[('', '---------')],
        coerce=int
    )

    admin_1_id = SelectField(
        _l('Nivel administrativo 1'),
        coerce=int,
        validators=[DataRequired(message=_l('Debe seleccionar una división de nivel 1.')), NumberRange(min=1, message='Debe seleccionar una división válida.')],
        choices=[] 
    )

    admin_2_id = SelectField(
        _l('Nivel administrativo 2'),
        coerce=int,
        validators=[DataRequired(message=_l('Debe seleccionar una división de nivel 2.')), NumberRange(min=1, message='Debe seleccionar una división válida.')],
        choices=[] 
    )

    ubi = StringField(
        _l('Nombre ubicación'),
        validators=[
            DataRequired(message=_l('El nombre de la ubicación es obligatorio.')),
            Length(max=255, message=_l('Máximo 255 caracteres.'))
        ]
    )

    latitude = StringField(
        _l('Latitud'),
        validators=[
            DataRequired(message=_l('La latitud es obligatoria.')),
            Length(max=20, message=_l('Máximo 20 caracteres.'))
        ]
    )

    longitude = StringField(
        _l('Longitud'),
        validators=[
            DataRequired(message=_l('La longitud es obligatoria.')),
            Length(max=20, message=_l('Máximo 20 caracteres.'))
        ]
    )

    altitude = StringField(
        _l('Altitud'),
        validators=[
            Length(max=20, message=_l('Máximo 20 caracteres.'))
        ]
    )


    visible = BooleanField(_l('¿Es visible?'), default=True)
    #enable = BooleanField(_l('¿Está habilitado?'), default=True)

    submit = SubmitField(_l('Guardar'))
