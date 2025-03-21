from flask import Flask, render_template, request, redirect, url_for
from flask import Flask, session
from flask_mail import Mail, Message

import pymysql
import os
import binascii
from config import Config
import requests

app = Flask(__name__)




@app.route('/display_cart', methods=['GET'])
def display_cart():
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("""SELECT * FROM Items """)
        items = cursor.fetchall() 
        connection.commit()  # Commit changes to the database
    connection.close()


    if items:
        return jsonify(items)
    else:
        return jsonify({"error": "User not found"}), 404

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
        values = cursor.fetchall()
        
        value = []
        #save books in a list whose stcok > 0
        for x in range(0,len(values)):
            if values[x]['stock'] > 0:
                value.append(values[x])
            else:
                pass

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
        value4 = cursor.fetchall()

        #we save the comments in a list
        comentarios = []
        for x in range(0,len(value4)):
            comentarios.append(value4[x]['comentario'])

    
        #rating
        cursor.execute("""SELECT * FROM Opiniones WHERE id_libro = %s  """, (INDICE))
        registros = cursor.fetchall() # VALUE =    [{'id_opinion': 1, 'estrellas': 4, 'id_libro': 1, 'id_usuario': 2}, {'id_opinion': 3, 'estrellas': 1, 'id_libro': 1, 'id_usuario': 2}, {'id_opinion': 4, 'estrellas': 1, 'id_libro': 1, 'id_usuario': 2}]
    
        #total votes
        reviews = len(registros)

        if len(registros)>0:
            total = 0

            for x in range(0,len(registros)):
                total += registros[x]['estrellas']
            TOTAL = total / len(registros)
        else:
            total =0
            TOTAL = total

    connection.close()

    star1 = 0
    star2 = 0
    star3 = 0
    star4 = 0
    star5 = 0

    for x in range(0,reviews):
        if registros[x]['estrellas'] == 5:
            star5 += 1
        elif registros[x]['estrellas'] == 4:
            star4 += 1
        elif registros[x]['estrellas'] == 3:
            star3 += 1
        elif registros[x]['estrellas'] == 2:
            star2 += 1
        elif registros[x]['estrellas'] == 1:
            star1 += 1



    return render_template('book_details_template.html', libros=value, costos=value2, Indice = INDICE, total = TOTAL, opiniones = comentarios , views = reviews, star_1 = star1, star_2 = star2, star_3 = star3, star_4 = star4, star_5 = star5)


@app.route('/buy_book', methods=['POST'])
def buy_book():

    INDICE = int(request.form['id_libro'])
    amount = int(request.form['NumeroCompras'])
    

    connection = get_db_connection()
    with connection.cursor() as cursor:
        #Substrac from libros stock
        cursor.execute("""SELECT stock FROM Libros WHERE id_libro = %s  """, (INDICE))
        value = cursor.fetchone()
        new_stock = value['stock'] - amount
        cursor.execute ("""UPDATE Libros SET stock = %s WHERE id_libro=%s""", (new_stock, INDICE))

        #cursor.execute("""DELETE FROM Libros WHERE stock = %s  """, (0))
        
        #add a record in Compras table
        #first get user id
        user_acount = session.get('correo')
        cursor.execute("""SELECT id_usuario FROM Usuarios WHERE correo = %s  """, (user_acount))
        value = cursor.fetchone()
        userID = value.get('id_usuario')

        cursor.execute("""SELECT precio FROM Costos WHERE id_libro = %s  """, (INDICE))
        price = cursor.fetchone()
        print("INDICE ==",INDICE)
        print("Price == ",price)
        bookprice = price.get('precio')
        bookprice = bookprice*amount

        cursor.execute('INSERT INTO Compras (libros_comprados,total, id_usuario, id_libro) VALUES (%s,%s,%s,%s)',(amount,bookprice ,userID, INDICE))

        #add one purchase to the user
        cursor.execute("""SELECT libros_comprados FROM Usuarios WHERE correo = %s  """, (user_acount))
        value = cursor.fetchone()

        if value.get('libros_comprados') == None:
            x = 1
            cursor.execute ("""UPDATE Usuarios SET libros_comprados = %s WHERE id_usuario=%s""", (x, userID))
        else:
            x = int(value.get('libros_comprados'))
            x += amount
            cursor.execute ("""UPDATE Usuarios SET libros_comprados = %s WHERE id_usuario=%s""", (x, userID))

        cursor.execute("""SELECT id_usuario FROM Usuarios WHERE correo = %s  """, (user_acount))
        value = cursor.fetchone()
        
        

        # Configuración del servidor de correo
        app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USERNAME'] = '20223tn080@utez.edu.mx'
        app.config['MAIL_PASSWORD'] = 'zdjk lpob yuxq yrtb'

       

        connection.commit()  # Commit changes to the database
    connection.close()

    mail = Mail(app)
    user_acount = session.get('correo')
    
    msg = Message(subject = 'Ticket de compra', sender='20223tn080@utez.edu.mx', recipients=[user_acount],body="This is the plain text body",html="<p>This is the HTML body</p>" )
    
    #mail.send(msg)
    return view_index(False)
    


@app.route('/template_add_cart')
def template_add_cart():
    #get items from the cart and send them to template_cart.html
    connection = get_db_connection()
    with connection.cursor() as cursor:

        #get nombre_libro, autor, imagen, precio 
        #get id_usuario
        user_acount = session.get('correo')      
        cursor.execute("""SELECT id_usuario FROM Usuarios WHERE correo = %s  """, (user_acount))
        value = cursor.fetchone()
        userID = value.get('id_usuario')

        cursor.execute("""SELECT id_libro FROM Items WHERE id_usuario = %s  """, (userID))
        booksIDS = cursor.fetchall() #BOOKSIDS ==  [{'id_libro': 2}, {'id_libro': 1}]
        print("booksIDS == ",booksIDS)
        print("LEN = ",len(booksIDS))

        #get prices
        prices =0
        for x in range(0,len(booksIDS)):
            cursor.execute("""SELECT precio FROM Costos WHERE id_libro = %s  """, (booksIDS[x]['id_libro']))
            books_prices = cursor.fetchall() 
            prices += books_prices[0]['precio']
    
        #save the books in a list to show them later 
        Libros = []
        for x in range(0,len(booksIDS)):
            cursor.execute("""SELECT nombre_libro, autor, imagen FROM Libros WHERE id_libro = %s  """, (booksIDS[x]['id_libro']))
            books = cursor.fetchall() # [{'nombre_libro': 'El pincipe', 'autor': 'Nicolas Maquiavelo', 'imagen': 'static/uploads\\libro2.jpg'}]
            Libros.append(books) # Libros = [[{'nombre_libro': 'El pincipe', 'autor': 'Nicolas Maquiavelo', 'imagen': 'static/uploads\\libro2.jpg'}], [{'nombre_libro': 'El capital', 'autor': 'Karl Marx', 'imagen': 'static/uploads\\libro1.jpg'}]]
        

        rango = len(Libros)
        #lets defined if there are books or not
        if len(Libros) > 0:
            cart = True
        else:
            cart = False

        


        connection.commit()  # Commit changes to the database
    connection.close()

    return render_template('template_cart.html',Books = Libros, rango = rango, cart = cart, total_price = prices)
    

@app.route('/add_cart', methods=['POST'])
def add_cart():
    #get id_libro
    INDICE = int(request.form['id_libro'])
    amount = int(request.form.get('NumeroCarrito'))

    print("COMPRAS : ",amount)

    connection = get_db_connection()
    with connection.cursor() as cursor:
        #get id_usuario
        user_acount = session.get('correo')      
        cursor.execute("""SELECT id_usuario FROM Usuarios WHERE correo = %s  """, (user_acount))
        value = cursor.fetchone()
        userID = value.get('id_usuario')

        #get id_precio
        cursor.execute("""SELECT id_precio FROM Costos WHERE id_libro = %s  """, (INDICE))
        value2 = cursor.fetchone()
        priceID = value2.get('id_precio')

        #insert into Items
        cursor.execute('INSERT INTO Items (id_usuario,cantidad,id_libro,id_precio) VALUES (%s,%s,%s,%s)',(userID,amount,INDICE,priceID))

        connection.commit()  # Commit changes to the database
    connection.close()

    return book_details()

@app.route('/buy_items')
def buy_items():
    connection = get_db_connection()
    with connection.cursor() as cursor:

        #get id_usuario
        user_acount = session.get('correo')      
        cursor.execute("""SELECT id_usuario FROM Usuarios WHERE correo = %s  """, (user_acount))
        value = cursor.fetchone()
        userID = value.get('id_usuario')
        #get id_libros
        cursor.execute("""SELECT id_libro FROM Items WHERE id_usuario = %s  """, (userID))
        booksIDS = cursor.fetchall() #BOOKSIDS ==  [{'id_libro': 2}, {'id_libro': 1}]

        AmountPerBook = []
        for x in range(0,len(booksIDS)):
            #get amount
            cursor.execute("""SELECT cantidad FROM Items WHERE id_libro = %s  """, (booksIDS[x]['id_libro']))
            booksAmount = cursor.fetchall() #BOOKSIDS ==  [{'id_libro': 2}, {'id_libro': 1}]
            AmountPerBook.append(booksAmount) # [[{'cantidad': 2}], [{'cantidad': 3}]]

        #get prices
        prices = []
        for x in range(0,len(booksIDS)):
            cursor.execute("""SELECT precio FROM Costos WHERE id_libro = %s  """, (booksIDS[x]['id_libro']))
            books_prices = cursor.fetchall() 
            prices.append(books_prices) # [[{'precio': 500.0}], [{'precio': 800.0}]]
    
        #record the purchases
        for x in range(0,len(booksIDS)):#                                                                                     libros comprados              total a pagar por libro                usuario      id libro
            cursor.execute('INSERT INTO Compras (libros_comprados, total, id_usuario, id_libro) VALUES (%s,%s,%s,%s)',(AmountPerBook[x][0]['cantidad'],(prices[x][0]['precio'])*(AmountPerBook[x][0]['cantidad']) ,userID, booksIDS[x]['id_libro']))


        #add purchases to the user
        cursor.execute("""SELECT libros_comprados FROM Usuarios WHERE correo = %s  """, (user_acount))
        value = cursor.fetchone()
        
        if value.get('libros_comprados') == None:
            z = 0
            for x in range(0,len(booksIDS)):
                z += AmountPerBook[x][0]['cantidad']
            cursor.execute ("""UPDATE Usuarios SET libros_comprados = %s WHERE id_usuario=%s""", (z, userID))
        else:
            z = int(value.get('libros_comprados'))
            z += AmountPerBook[x][0]['cantidad']
            cursor.execute ("""UPDATE Usuarios SET libros_comprados = %s WHERE id_usuario=%s""", (z, userID))

        #delete records from Items
        for x in range(0,len(booksIDS)):
            cursor.execute("""DELETE  FROM Items WHERE id_libro = %s  """, (booksIDS[x]['id_libro']))

        #delete books stock 
        for x in range(0,len(booksIDS)):
            cursor.execute("""SELECT stock FROM Libros WHERE id_libro = %s  """, (booksIDS[x]['id_libro']))
            value = cursor.fetchone()
            new_stock = value['stock'] - AmountPerBook[x][0]['cantidad']
            cursor.execute ("""UPDATE Libros SET stock = %s WHERE id_libro=%s""", (new_stock, booksIDS[x]['id_libro']))


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

        #evaluate if the user had already voted
        cursor.execute("""SELECT id_usuario FROM Opiniones WHERE id_libro = %s  """, (INDICE))
        opinions = cursor.fetchall() # [{'id_usuario':x},{'id_usuario':y}, {'id_usuario':z} ] 
        print("existe una opinion del usuario actual  ==  ",opinions)

       

        lista = []
        for x in range(0,len(opinions)):
            lista.append(opinions[x]['id_usuario'])

        print("LISTA DE LOS IDS DE USUARIOS  == ",lista)
    
        if userID in lista: # the user had already voted
            cursor.execute ("""UPDATE Opiniones SET estrellas = %s, comentario = %s  WHERE id_libro=%s""", (rating, comentario, INDICE))
        else:
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
