from flask import Flask, render_template, request, flash # Agregamos el modulo flash
from flask_wtf import FlaskForm # Importamos FlaskForm
from wtforms import StringField, SubmitField # Importamos los campos StringField y SubmitField
from wtforms.validators import DataRequired, ValidationError, Regexp # Importamos los validadores DataRequired y Regexp
import requests

app = Flask(__name__) # Creamos una instancia de Flask
app.config['SECRET_KEY'] = 'tu_clave_secreta' # Agregamos una clave secreta

class LengthValidator(object): # Creamos una clase LengthValidator
    def __init__(self, min=-1, max=-1):  # Damos valores por defecto a min y max
        self.min = min 
        self.max = max

    def __call__(self, form, field): # Creamos un método __call__
        length = field.data and len(field.data) or 0
        if length < self.min or (self.max != -1 and length > self.max): # Comprobamos si el campo cumple con la condición
            raise ValidationError('El campo debe tener entre %i y %i caracteres.' % (self.min, self.max)) # Lanzamos una excepción si no se cumple la condición

class ConsultaForm(FlaskForm): # Creamos una clase ConsultaForm que hereda de FlaskForm
    num_documento = StringField('Número de documento', validators=[DataRequired(), LengthValidator(min=6), Regexp(r'^\d+$', message='El número de documento solo puede contener dígitos.')])
    # Creamos un campo num_documento de tipo StringField con una etiqueta y validadores
    submit = SubmitField('Consultar') # Creamos un campo submit de tipo SubmitField en el que se muestra el texto 'Consultar'

def obtener_estudiante_aprobado(num_documento): # Creamos una función obtener_estudiante_aprobado que recibe un número de documento
    url = "https://api.talentotech.cymetria.com/api/v1/blockchain/obtener-estudiantes-aprobados" # Definimos la URL de la API
    try:
        respuesta = requests.get(url) # Realizamos una solicitud GET a la API
        data = respuesta.json() # Obtenemos los datos de la respuesta en formato JSON
    except requests.exceptions.RequestException as e:
        flash('Hubo un error al hacer la solicitud a la API', 'error') # Mostramos un mensaje de error en caso de fallo
        return None # Retornamos None en caso de error

    for estudiante in data['estudiantes_aprobados']: # Iteramos sobre la lista de estudiantes aprobados
        if estudiante['estudiante']['num_documento'] == num_documento: # Comparamos el número de documento
            return { # Retornamos datos específicos del estudiante
                'nombre_completo': estudiante['estudiante']['nombres'] + ' ' + estudiante['estudiante']['apellidos'],
                'num_documento': estudiante['estudiante']['num_documento'],
                'correo_electronico': estudiante['estudiante']['email'],
                'nombre_curso': estudiante['curso']['nombreCurso'],
            }

    return None

@app.route('/', methods=['GET', 'POST']) # Definimos una ruta raíz con los métodos GET y POST
def consulta():
    form = ConsultaForm() # Creamos una instancia del formulario ConsultaForm
    estudiante = None
    if form.validate_on_submit():
        estudiante = obtener_estudiante_aprobado(form.num_documento.data) # Obtenemos los datos del estudiante aprobado
    return render_template('consulta.html', form=form, estudiante=estudiante) # Renderizamos la plantilla consulta.html con el formulario y los datos del estudiante

if __name__ == '__main__': 
    app.run(debug=True) # Ejecutamos la aplicación en modo debug