from click import edit
from flask import Flask #importo modulos
from flask import render_template #me ayuda a renderizar, a mostrar graficamente desde el backend
from flaskext.mysql import MySQL
from flask import render_template, request, redirect, url_for, flash
from datetime import datetime #para que las imagenes no se me repitan, coloco este modulo, cada IMAGEN SEA UNICA
import os #lo necesito para poder realizar la modificacion de mi imagen, asi logrando que la anterior imagen se elimine y se mantenga solo la nueva
from flask import send_from_directory #para que pueda acceder a la carpeta y mostrarse la imagen

app = Flask (__name__) #instancio, app = variable y app va a ser el nombre por eso entre parentesis de flask coloco (__name__)

app.secret_key = 'Clave' #para que mi cont viaje encriptado, no viaje libre


#gestionar la conexion con la BD
mysql = MySQL ()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_BD'] = 'netflax'
mysql.init_app(app) #inicializo el objeto mysql

CARPETA = os.path.join('uploads') #guardo en mi var CARPETA, la nueva imagen actualizada
app.config['CARPETA'] = CARPETA #parametros de config de nuestra app

@app.route('/uploads/<nombreimg>') #viendo como hacer para que se vea mi imagen
def uploads(nombreimg):
    return send_from_directory(app.config['CARPETA'], nombreimg) #asi accedemos a la carpeta desde la web

@app.route('/') #decorador, para mostrar como va a acceder a mi app
def index(): #metodo index, lo utilice solamente para verificar que la conexion este correcta
    sql= "SELECT * FROM netflax.peliculas;" #select
    conn = mysql.connect() #conexion con mi base de datos
    cursor = conn.cursor() #a mi conexion le pido un cursor
    cursor.execute(sql) #mi cursor es el encargado de ejecutar my sql
    pelis = cursor.fetchall() #le pido al cursor que me traiga todos los registros, le pido los datos
    # print(pelis)
    return render_template ('peliculas/index.html', pelis = pelis) #retorna el template renderizado, para q pueda visualizar
                                                     
@app.route('/create')
def create():
    return render_template('peliculas/create.html')

@app.route('/store', methods = ['POST'] ) #le aclaro q es un metodo post, que va a recibir info (de create.html) y va a tener que procesarla
def store():
    _nombre =request.form['txtnombre']
    _desc= request.form['txtdesc']
    _foto= request.files['txtimagen']


    if _nombre == '' or _desc == '' or _foto == '':
        flash("faltan datos obligatorios!")
        return redirect (url_for ('create'))
    now = datetime.now() #saco del modulo datetime y invoco el metodo now me devuelve el tiempo actual
    tiempo = now.strftime("%Y%H%M%S") #formateo el tiempo 
    if _foto.filename != '':
        nuevo_nombre_foto = tiempo + _foto.filename #concateno el tiempo con el nombre de la imagen
        _foto.save("uploads/" + nuevo_nombre_foto) #el metodo save lo que hace es tomar ese archivo y me lo guarda en la carpeta, con el tiempo y el nombre adjuntados en esa variable
    datos = (_nombre, _desc, nuevo_nombre_foto) #tupla, empaqueto los datos
    sql= "INSERT INTO netflax.peliculas(`nombre`, `descripcion`, `imagen`) VALUES (%s, %s, %s)"
                                                                            #orden para mis datos
    conn = mysql.connect() #conexion con mi base de datos
    cursor = conn.cursor() #a mi conexion le pido un cursor
    cursor.execute(sql, datos) #mi cursor es el encargado de ejecutar my sql
                               #la info para completar mi sql la saco de datos
    conn.commit() #grabo la transaccion

    #return render_template ('peliculas/index.html') #retorna el template renderizado, para q pueda visualizar
    return redirect('/') #para que me redireccione a la home
@app.route('/destroy/<int:id>') #como va a recibir un dato a traves de la URL, lo tengo que especificar que va a aser de tipo entero, y sera el id
def destroy(id): #cuando invoque a destroy, le voy a pasar tambien un id, el metodo lo debe tomar para hacer el delete de ese registro
    conn = mysql.connect() #conexion con mi base de datos
    cursor = conn.cursor()
    #elimino la imágen que esta en uploads
    cursor.execute("SELECT imagen FROM netflax.peliculas WHERE id=%s", id) #utilizo el id ya que es el parametro que nunca cambia
                                                        #selecciono la imagen que tengo
    img = cursor.fetchone() #
    os.remove(os.path.join(app.config['CARPETA'], img[0])) #remuevo la imagen fisicamente de la carpeta
    cursor.execute("DELETE FROM netflax.peliculas WHERE id=%s", (id)) #elimina donde el id sea igual al que te pase
                                                                #tupla, variable que recibe el metodo
                                                                #elimino la carpeta
    conn.commit()
    return redirect ('/')
@app.route('/edit.html/<int:id>')
def edit(id):
    conn = mysql.connect() #conexion con mi base de datos
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM netflax.peliculas WHERE id=%s", (id))
    peli = cursor.fetchone() #una tupla solamente el fetchone
    #conn.commit(), estoy consultando, no tengo que commitear nada
    return render_template ('peliculas/edit.html', peli = peli )
@app.route('/update', methods = ['POST'] ) #le aclaro q es un metodo post, que va a recibir info (de create.html) y va a tener que procesarla
def update():
    #declaro variables primero
    _nombre =request.form['txtnombre']
    _desc= request.form['txtdesc']
    _foto= request.files['txtimagen']  #primero, tomo los NUEVOS DATOS que cargué en mi form (/update), edit.html
    _ID= request.form['txtID']
    now = datetime.now() #saco del modulo datetime y invoco el metodo now me devuelve el tiempo actual
    tiempo = now.strftime("%Y%H%M%S") #formateo el tiempo
    if _foto.filename != '': #si me selecciono una imagen
        nuevo_nombre_foto = tiempo + _foto.filename #guado todo en una nueva variable, concatenando el tiempo asignado y el nombre del archivo
        _foto.save("uploads/" + nuevo_nombre_foto) #subo la nueva foto
    sql= "UPDATE netflax.peliculas SET nombre = %s, descripcion = %s, imagen=%s WHERE id = %s;"
    #segundo, guardo los nuevos datos en varible datos
    datos= ( _nombre, _desc, nuevo_nombre_foto, _ID)
    conn = mysql.connect() #conexion con mi base de datos
    cursor = conn.cursor() #a mi conexion le pido un cursor
    cursor.execute("SELECT imagen FROM netflax.peliculas WHERE id=%s", _ID) #utilizo el id ya que es el parametro que nunca cambia
                                                        #esta accion la hago ANTES de actualizar mis datos
    img = cursor.fetchone() #tomo el nombre de la imagen que tengo (no la nueva). 
    os.remove(os.path.join(app.config['CARPETA'], img[0])) #elimino la imagen anterior
    #coloco como variable la accion q se va a ejercer en el sql
    sql= "UPDATE netflax.peliculas SET nombre = %s, descripcion = %s, imagen=%s WHERE id = %s;"
    #segundo, guardo los nuevos datos en varible datos
    datos= ( _nombre, _desc, nuevo_nombre_foto, _ID)
    cursor.execute(sql, datos) #mi cursor es el encargado de ejecutar my sql
                               #la info para completar mi sql la saco de datos
                               #actualizo los datos
    conn.commit() #grabo la transaccion
    return redirect ('/')



# http://127.0.0.1:5000/
if __name__ == '__main__': #ejecuta solo si ejecutamos desde este modulo, evita cuando importe que se ejecute lo de abajo
    app.run (debug=True) #para ejecutar


