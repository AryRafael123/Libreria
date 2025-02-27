from flask import Flask, render_template, request, redirect, url_for
from flask import Flask, session
import pymysql
import os
import binascii
from config import Config


app = Flask(__name__)

app.secret_key = binascii.hexlify(os.urandom(24)).decode() # Necesario para usar sesiones

#MySQL connection settings
def get_db_connection():
    connection = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='mysqlpassword123',
        db='Librería',
        cursorclass=pymysql.cursors.DictCursor  # To get results as dictionaries
    )
    return connection



@app.route('/')
def index():
    if not session:
        #session empy, so sign in
        return render_template('index.html')
    else:
        #one session before, so let's find out the user type
        # let's create the conection with our data base
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT tipo_usuario, correo, contraseña FROM Usuarios')
            value = cursor.fetchall()
        connection.close()

        #we need to find out the "tipo_usuario" value
        for x in range(0,len(value)):
            if value[x]["correo"] == session["correo"]:
                if value[x]["tipo_usuario"] == 1: #we know the index user of the session
                    #admin user
                    return render_template('index_admin.html')
                else:
                    #normal user
                    return render_template('index_user.html')
               



@app.route('/sign_in', methods=['POST'])
def add_user():


    mail = request.form['mail']
    password = request.form['password']

    
    # Insert the new user into the database
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute('SELECT tipo_usuario, correo, contraseña FROM Usuarios')
        value = cursor.fetchall()
        connection.close()
        
    sesion = False
    existe = False
    admin = False
    
    for x in range(0,len(value)):
        if value[x]["contraseña"] == password and value[x]["correo"] == mail:
            #el usuario existe
            existe = True
            sesion = True
            session['correo'] = mail
            if value[x]["tipo_usuario"]==True:
                #usuario administrador
                admin = True
                session['correo'] = mail
            else:
                print("")
        else:
            print("")
            
    
    print("existe: ",existe)
    print("administrador: ",admin)
    print("correo",mail)
    print("sesion: ",session)
    print("secret key: ", app.secret_key)


    if existe == True:
        if admin == True:
            return render_template('index_admin.html')
        else:
            return render_template('index_user.html')
    else:
        return render_template('index.html')
        



@app.route('/template_sign_up',methods=['POST'])
def SIGN_UP2():
    return render_template('add_user.html')



@app.route('/sign_up', methods=['POST'])
def ADD_USER2():

# This is the form data that Flask receives
    name = request.form['name']  # Flask looks for the 'username' key
    last_name = request.form['last_name']
    user_name = request.form['user_name']
    address = request.form['address']
    phone = request.form['phone']
    mail = request.form['mail']
    password = request.form['password']
    
    # Insert the new user into the database
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO Usuarios (tipo_usuario, nombre, apellido, nombre_usuario, direccion, teléfono, correo, contraseña) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',(False, name, last_name, user_name, address, phone, mail, password))
        connection.commit()  # Commit changes to the database
    connection.close()

    return render_template('index.html')




@app.route('/log_out')
def LOG_OUT():
    #eliminar la variable sesion
   
    session.popitem()
    
    return render_template('index.html')


@app.route('/add_user', methods=['POST'])
def ADD_USER():

# This is the form data that Flask receives
    name = request.form['name']  # Flask looks for the 'username' key
    last_name = request.form['last_name']
    user_name = request.form['user_name']
    address = request.form['address']
    phone = request.form['phone']
    mail = request.form['mail']
    password = request.form['password']
    
    # Insert the new user into the database
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO Usuarios (tipo_usuario, nombre, apellido, nombre_usuario, direccion, teléfono, correo, contraseña) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',(True, name, last_name, user_name, address, phone, mail, password))
        connection.commit()  # Commit changes to the database
    connection.close()

    return render_template('index.html')



#This action takes to the template of add user (edit user)
@app.route('/template_edit_user')
def template_edit_user():

    return render_template('edit_user.html')



@app.route('/edit_user', methods=['POST'])
def EDIT_USER():
    mail = session["correo"]

    # This is the form data that Flask receives
    new_name = request.form['name']  # Flask looks for the 'username' key
    new_last_name = request.form['last_name']
    new_user_name = request.form['user_name']
    new_address = request.form['address']
    new_phone = request.form['phone']
    new_mail = request.form['mail']
    new_password = request.form['password']
        
    connection = get_db_connection()
    with connection.cursor() as cursor:
       
        cursor.execute ("""UPDATE Usuarios SET nombre=%s, apellido=%s, nombre_usuario=%s, direccion=%s, teléfono=%s, correo=%s, contraseña=%s WHERE correo=%s""", (new_name, new_last_name, new_user_name, new_address, new_phone,new_mail, new_password, mail))
        connection.commit()
        connection.close()

    return render_template('index.html')



if __name__ == '__main__':
    app.run(debug=True)

#CODE TO GENERATE SECURE KEYS

secretkey = binascii.hexlify(os.urandom(24)).decode()

print(secret_key) #No es nesesario agregar esta linea, solo para verificar.
