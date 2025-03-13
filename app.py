from flask import Flask, render_template, request, redirect, url_for
from flask import Flask, session
import pymysql
import os
import binascii
from config import Config

app = Flask(__name__)


# Configurations to add a image to a book
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}


# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


app.secret_key = binascii.hexlify(os.urandom(24)).decode() # Necesario para usar sesiones


#MySQL connection settings
def get_db_connection():
    connection = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='root',
        db='libreria',
        cursorclass=pymysql.cursors.DictCursor  # To get results as dictionaries
    )
    return connection

#Función para mostrar la vista Admin/Usuario
def view_index(admin):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM libros ORDER by id_libro DESC')
        value = cursor.fetchall()
        connection.close()
    
    if admin == True:
        #return url_for('/admin')
        return render_template('index_admin.html', data=value)
    else:
        return render_template('index_user.html', data=value)


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
                    return view_index(True)
                else:
                    #normal user
                    return view_index(False)
               

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
            #return url_for('/admin')
            return view_index(admin)
        else:
            return view_index(admin)
            #return render_template('index_user.html')
    else:
        return render_template('index.html')


@app.route('/template_sign_up')
def SIGN_UP2():
    return render_template('add_user.html')


@app.route('/sign_up', methods=['POST'])
def ADD_USER2():

    #This is the form data that Flask receives
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


@app.route('/delete_book', methods=['POST'])
def delete_book():

    INDICE = int(request.form['id_libro'])

    #print("ID LIBRO ES  :",IDlibro, "Y ES DE TIPO",type(IDlibro) )
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("""DELETE FROM Libros WHERE id_libro = %s  """, (INDICE))
        connection.commit()
        connection.close()

    return view_index(True)


@app.route('/add_book', methods=['POST'])
def ADD_BOOK():
    
#CODE TO ADD A IMAGE TO A BOOK
    image = request.files.get('image')
    print("ARRIBA LAS CHIVAS")
    print ("image: ",image)
    #save the image if is allowed
    if image and allowed_file(image.filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(filename)
    print("filename = ",filename)

# CODE TO ADD A BOOK
    name_book = request.form['book-title']  
    autor = request.form['book-autor']
    editorial = request.form['book-editorial']
    stock = request.form['book-stock']
    price = request.form['book-price']
    description = request.form['book-description']

    # Insert the new user into the database
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO Libros (nombre_libro, autor, editorial, stock, imagen, descripcion) VALUES (%s,%s,%s,%s,%s,%s)',(name_book, autor, editorial, stock,filename, description))
        cursor.execute('SELECT id_libro FROM Libros')
        value = cursor.fetchone() 
        x = value["id_libro"]
        x = int(x)
        print("x = ",x)
        cursor.execute('INSERT INTO Costos (precio,id_libro) VALUES (%s,%s)',(price,x))
        cursor.execute('SELECT id_precio FROM Costos ORDER by id_precio DESC LIMIT 1')
        value1 = cursor.fetchone() 
        y = value1["id_precio"]
        y = int(y)
        print("x = ",y)
        cursor.execute ("""UPDATE Libros SET id_precio = %s WHERE id_libro=%s""", (y, x))
        connection.commit()  # Commit changes to the database
    connection.close()

    return view_index(True)

@app.route('/book_details', methods=['POST'])
def book_details():

    INDICE = int(request.form['id_libro'])
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("""SELECT * FROM Libros WHERE id_libro = %s  """, (INDICE))
        value = cursor.fetchone()
        cursor.execute("""SELECT * FROM Costos WHERE id_libro = %s  """, (INDICE))
        value2 = cursor.fetchone()

        cursor.execute("""SELECT * FROM Opiniones WHERE id_libro = %s  """, (INDICE))
        value4 = cursor.fetchone()


        #rating
        cursor.execute("""SELECT * FROM Opiniones WHERE id_libro = %s  """, (INDICE))
        value3 = cursor.fetchall() # VALUE =    [{'id_opinion': 1, 'estrellas': 4, 'id_libro': 1, 'id_usuario': 2}, {'id_opinion': 3, 'estrellas': 1, 'id_libro': 1, 'id_usuario': 2}, {'id_opinion': 4, 'estrellas': 1, 'id_libro': 1, 'id_usuario': 2}]
    
        if len(value3) >1:
            total = 0
            for x in range(0,len(value3)):
                total += value3[x]['estrellas']
            TOTAL = total / len(value3)
        else:
            total =0
            TOTAL = total

    connection.close()

    return render_template('book_details_template.html', data=value, data2=value2, Indice = INDICE, total = TOTAL, data3 = value4 )


@app.route('/buy_book', methods=['POST'])
def buy_book():

    INDICE = int(request.form['id_libro'])

    connection = get_db_connection()
    with connection.cursor() as cursor:
        #Substrac 1 from libros stock
        cursor.execute("""SELECT stock FROM Libros WHERE id_libro = %s  """, (INDICE))
        value = cursor.fetchone()
        new_stock = value['stock'] - 1
        cursor.execute ("""UPDATE Libros SET stock = %s WHERE id_libro=%s""", (new_stock, INDICE))

        print("VALUE = ",value)

        #add a record in Compras table
        #first get user id
        user_acount = session.get('correo')
        
        cursor.execute("""SELECT id_usuario FROM Usuarios WHERE correo = %s  """, (user_acount))
        value = cursor.fetchone()
        userID = value.get('id_usuario')
        cursor.execute("""SELECT precio FROM Costos WHERE id_libro = %s  """, (INDICE))
        value = cursor.fetchone()
        bookprice = value.get('precio')

        cursor.execute('INSERT INTO Compras (total, id_usuario, id_libro) VALUES (%s,%s,%s)',(bookprice ,userID, INDICE))

        #add one purchase to the user
        cursor.execute("""SELECT libros_comprados FROM Usuarios WHERE correo = %s  """, (user_acount))
        value = cursor.fetchone()

        if value.get('libros_comprados') == None:
            x = 1
            cursor.execute ("""UPDATE Usuarios SET libros_comprados = %s WHERE id_usuario=%s""", (x, userID))
        else:
            x = int(value.get('libros_comprados'))
            x += 1
            cursor.execute ("""UPDATE Usuarios SET libros_comprados = %s WHERE id_usuario=%s""", (x, userID))


        connection.commit()  # Commit changes to the database
    connection.close()

    return view_index(False)
    
@app.route('/template_purchases')
def template_purchases():
    connection = get_db_connection()
    with connection.cursor() as cursor:  
        #get user id
        user_acount = session.get('correo')  
        cursor.execute("""SELECT id_usuario FROM Usuarios WHERE correo = %s  """, (user_acount))
        value = cursor.fetchone()
        userID = value.get('id_usuario')

        #lets get all purchases from the data base 
        cursor.execute("""SELECT id_libro FROM Compras WHERE id_usuario = %s  """, (userID))
        values = cursor.fetchall()
        print('VALUES = ',values) # VALUES =  [{'id_libro': x}, {'id_libro': y}, {'id_libro':z}]

        indices =[]
        for x in range(0,len(values)): 
            indices.append(int(values[x]['id_libro']))  # indices = [x,y]
    
        print("LISTA INDICESSSSS:  ",indices, "tipo: ",type(indices))

        books = []
        for x in range(0,len(indices)):
            cursor.execute("""SELECT * FROM Libros WHERE id_libro = %s  """, (indices[x]))
            values = cursor.fetchall()
            books.append(values) # books = [ [{}] , [{}]  ]
        rango = len(books)
        cursor.execute("""SELECT * FROM Libros WHERE id_libro = %s  """, (userID))

    
    return render_template('template_purchases.html', BOOKS = books, rango = rango) 



@app.route('/book_rating', methods=['POST'])
def book_rating():
    INDICE = int(request.form['id_libro'])
    rating = request.form['rating']
    comentario = request.form['comment']
    
    connection = get_db_connection()
    with connection.cursor() as cursor:  
        #get user id
        user_acount = session.get('correo')  
        cursor.execute("""SELECT id_usuario FROM Usuarios WHERE correo = %s  """, (user_acount))
        value = cursor.fetchone()
        userID = value.get('id_usuario')

        cursor.execute('INSERT INTO Opiniones (estrellas, id_libro, id_usuario, comentario) VALUES (%s,%s,%s,%s)',(rating ,INDICE, userID, comentario))

        connection.commit()  # Commit changes to the database
    connection.close()



    return template_purchases()






#@app.route('/admin')
#def prueba():
#    return view_index_admin()

if __name__ == '__main__':
    app.run(debug=True)

#CODE TO GENERATE SECURE KEYS

secretkey = binascii.hexlify(os.urandom(24)).decode()

print(secret_key) #No es nesesario agregar esta linea, solo para verificar.
