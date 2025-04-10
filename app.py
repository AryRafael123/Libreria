from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import Flask, session
from flask_mail import Mail, Message
import pymysql
import os
import binascii
from config import Config
import requests
import yaml
import paypalrestsdk
import math
#HASSIEL

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)

# PayPal API Credentials (Replace with your sandbox credentials)
#PAYPAL_CLIENT_ID = "AbducxexQw-HObCokRA9XyCiXRiKyprjWc7FxOKhBQGKZlIAheWIRrs_R6fZ1MUQwXTE4K3uY2fafUGF"
#PAYPAL_SECRET = "EOcXBp8S96NQl6YSz9CbMQ954XjWT0JuJiUgDDYPLoaCB82hVqinjs21JqBMDlv9f8fPGBvvsI5pzf6d"
PAYPAL_CLIENT_ID = "AVuuO9ebw5JS7AptdgDMyhQ14Knq3udTdRxTB3RZfkp8rIEQyQYwpaPH5PzQizyXubwN5xHsmyx58oW-"
PAYPAL_SECRET = "EM438loYDqhR55FrnTEiezbsmAMb9-B4247yUeJ0mJgFY8RSsqunBmZotxpgxDtW1MghjuYTNS7OAorT"
PAYPAL_API_BASE = "https://sandbox.paypal.com"  # Sandbox URL

#code to send an email
# Configuración del servidor de correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '20223tn080@utez.edu.mx'
app.config['MAIL_PASSWORD'] = 'zdjk lpob yuxq yrtb'    


# route to redirect a user 
@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('index'))

# Function to get PayPal access token
def get_paypal_access_token():
    auth = (PAYPAL_CLIENT_ID, PAYPAL_SECRET)
    response = requests.post(f"{PAYPAL_API_BASE}/v1/oauth2/token",
                             data={"grant_type": "client_credentials"},
                             auth=auth)
    return response.json().get("access_token")


# Route to create an order
@app.route("/create_order", methods=["POST"])
def create_order():
    data = request.get_json()
    precio_libro = data['precio']
    access_token = get_paypal_access_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {"currency_code": "MXN", "value": precio_libro}  # Change amount here
        }]
    }
    response = requests.post(f"{PAYPAL_API_BASE}/v2/checkout/orders", json=data, headers=headers)
    return jsonify(response.json())

# Route to capture payment
@app.route("/capture-order/<order_id>", methods=["POST"])
def capture_order(order_id):
    access_token = get_paypal_access_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.post(f"{PAYPAL_API_BASE}/v2/checkout/orders/{order_id}/capture", headers=headers)
    return jsonify(response.json())


# Load labels from YAML file
def load_labels():
    with open("labels.yaml", "r") as file:
        return yaml.safe_load(file)

# Save labels to YAML file
def save_labels(data):
    with open("labels.yaml", "w") as file:
        yaml.safe_dump(data, file)



@app.route('/display_cart', methods=['GET'])
def display_cart():
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("""SELECT * FROM Items """)
        Items = cursor.fetchall() 
        connection.commit()  # Commit changes to the database
    connection.close()


    if Items:
        return jsonify(Items)
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
        host='libreria.cit0xrarrrli.us-east-1.rds.amazonaws.com',
        user='root',
        password='Libreria2025',
        db='libreria',
        cursorclass=pymysql.cursors.DictCursor  # To get results as dictionaries
    )
    return connection

#Función para mostrar la vista Admin/Usuario
def view_index(admin):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM Libros ORDER by id_libro DESC')
        values = cursor.fetchall()
        
        value = []
        #save books in a list whose stcok > 0
        for x in range(0,len(values)):
            if values[x]['stock'] > 0:
                value.append(values[x])
            else:
                pass

        connection.close()

    #code to show the books 5 and 5
    num = (len(values))/5
    vueltas = math.ceil(num)
    #value [] = [{libro1}, {libro2} ,{libro3}, {libro4}, {libro5}, {libro6}]
    block = [] # [{libro1}, {libro2}, {libro3}, {libro4}, {libro5}]
    row_list = [] # *[*  [{libro1}, {libro2}, {libro3}, {libro4}, {libro5}], [{libro1}, {libro2}, {libro3}, {libro4}, {libro5}], [{libro1}, {libro2}]  *]*
   # code to encapsulate books in groups of 5
    x = 0
    while x < len(value):
        if len(block) <= 4:
            block.append(value[x])
            if x == len(value)-1:
                row_list.append(block)
                block = []
            else:
                pass
            if len(block) == 5:
                row_list.append(block)
                block = []
            else:
                pass
        else:
            pass
        x+=1
    
    if admin == True:
        #return url_for('/admin')
        return adminHome()
        #return render_template('admin.html', data=value)
    else:
        return render_template('index_user.html', data=value, labels = load_labels(), turns = vueltas, allbooks = row_list )

@app.route('/adminHome')
def adminHome():
    id_usuario = session.get('id_usuario')
    nombre = session.get('nombre_usuario')
    apellido = session.get('apellido_usuario')

    nombre_completo = nombre+" "+apellido

    return render_template('admin_home.html', nombre = nombre_completo)

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
               

@app.route('/template_labels')
def template_labels():

    labels = load_labels()

    return render_template('form.html', labels = load_labels() )

@app.route('/change_labels', methods=['POST'])
def change_labels():

    labels = load_labels()

    # Update labels with form data
    labels["buttons"]["buy"] = request.form["buy books"]
    labels["buttons"]["logout"] = request.form["log out"]
    labels["buttons"]["search"] = request.form["search"]

    save_labels(labels)  # Save updated labels to YAML

    return view_index(False)


@app.route('/sign_in', methods=['POST'])
def add_user():

    mail = request.form['mail']
    password = request.form['password']

    # Insert the new user into the database
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute('SELECT id_usuario, tipo_usuario, correo, contraseña, nombre, apellido FROM Usuarios')
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
            session['id_usuario'] = value[x]["id_usuario"]
            session['nombre_usuario'] = value[x]["nombre"]
            session['apellido_usuario'] = value[x]["apellido"]
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
   
    #session.popitem()
    session.clear()
    
    return render_template('index.html')


@app.route('/create_account', methods=['POST'])
def create_account():

    # This is the form data that Flask receives
    name = request.form['name']  # Flask looks for the 'username' key
    last_name = request.form['last_name']
    user_name = request.form['user_name']
    address = request.form['address']
    phone = request.form['phone']
    email = request.form['email']
    password = request.form['password']
    
    exist = False
    print("ADENTROO")

    # Insert the new user into the database
    connection = get_db_connection()
    with connection.cursor() as cursor:

        cursor.execute("""SELECT * FROM Usuarios WHERE correo = %s  """, (email))
        value = cursor.fetchone()

        if value == None:
            cursor.execute('INSERT INTO Usuarios (tipo_usuario, nombre, apellido, nombre_usuario, direccion, teléfono, correo, contraseña) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',(False, name, last_name, user_name, address, phone, email, password))
            connection.commit()
            connection.close()
            return jsonify({'exists': False, 'redirect_url': url_for('index')})
            
        else:
            connection.close()
            return jsonify({'exists': True})
            
    


#This action takes to the template of add user (edit user)
@app.route('/template_edit_user')
def template_edit_user():

    #we send the values of the user 
    user_id = session.get('id_usuario') 

    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("""SELECT * FROM Usuarios WHERE id_usuario = %s  """, (user_id))
        value = cursor.fetchone() # {'id_usuario': 1, 'tipo_usuario': 0, 'nombre': 'Ary Rafael', 'apellido': 'Sánchez Hernández', 'nombre_usuario': 'Ary123', 'direccion': 'Morelos', 'teléfono': '7775955444', 'correo': '20223tn078@utez.edu.mx', 'contraseña': 'ary12345', 'Libros_comprados': None, 'id_opinion': None}
        connection.commit()
    connection.close()


    return render_template('edit_user.html', labels = load_labels(), data = value)

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

@app.route('/templates_edit_book', methods=['POST'])
def templates_edit_book():
    id_libro2 = request.form['id_libro']
    return render_template('edit_book.html',id=id_libro2)

@app.route('/edite_book', methods=['POST'])
def EDITE_BOOK():
    INDICE = int(request.form['ID_LIBRO'])
    image = request.files.get('image')
    if image and allowed_file(image.filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(filename)
    print("filename = ",filename)
    # This is the form data that Flask receives
    new_name = request.form['name']  # Flask looks for the 'username' key
    new_autor = request.form['autor']
    new_editorial = request.form['editorial']
    new_descripcion = request.form['descripcion']
    new_precio = request.form['precio']
        
    connection = get_db_connection()
    with connection.cursor() as cursor:
       
        cursor.execute ("""UPDATE Libros SET nombre_libro=%s, autor=%s, editorial=%s,descripcion=%s, imagen=%s  where id_libro = %s""", (new_name,new_autor,new_editorial,new_descripcion,filename,INDICE))
        cursor.execute ("""UPDATE Costos SET precio=%s where id_libro = %s""", (new_precio,INDICE))
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
        print("COSTOS ",value2)
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



    return render_template('book_details_template.html',client_id=PAYPAL_CLIENT_ID, Libros=value, Costos=value2, Indice = INDICE, total = TOTAL, Opiniones = comentarios , views = reviews, star_1 = star1, star_2 = star2, star_3 = star3, star_4 = star4, star_5 = star5, labels = load_labels())


@app.route('/buy_book', methods=['POST'])
def buy_book():

    data = request.get_json()


    connection = get_db_connection()
    with connection.cursor() as cursor:
        #Substrac from Libros stock
        cursor.execute("""SELECT stock FROM Libros WHERE id_libro = %s  """, (INDICE))
        value = cursor.fetchone()
        new_stock = value['stock'] - amount
        cursor.execute ("""UPDATE Libros SET stock = %s WHERE id_libro=%s""", (new_stock, INDICE))

        
        #update or insert a record in Compras table
        #get user id : > userID <
        user_acount = session.get('correo')
        cursor.execute("""SELECT id_usuario FROM Usuarios WHERE correo = %s  """, (user_acount))
        value = cursor.fetchone()
        userID = value.get('id_usuario')
        #get book price: > bookprice <
        cursor.execute("""SELECT precio FROM Costos WHERE id_libro = %s  """, (INDICE))
        price = cursor.fetchone()
        print("INDICE ==",INDICE)
        print("Price == ",price)
        bookprice = price.get('precio')
        book_price = price.get('precio')
        bookprice = bookprice*amount

    
        Book = False
        #evaluate if the book id is in Compras table
        cursor.execute("""SELECT id_libro FROM Compras """)
        value = cursor.fetchall() # [{'id_libro': 1},{'id_libro': 2}] / none
        if value == None:
            pass
        else:
            for x in range(0,len(value)):
                if value[x]['id_libro'] == INDICE:
                    book = True
                else:
                    pass
    
        if Book == False: # the book is not in Compras table
            cursor.execute('INSERT INTO Compras (Libros_comprados,total, id_usuario, id_libro) VALUES (%s,%s,%s,%s)',(amount,bookprice ,userID, INDICE))
        else: #we update the table
            cursor.execute("""SELECT Libros_comprados FROM Compras WHERE id_libro = %s  """, (INDICE))
            books_purchased = cursor.fetchone()
            purchasedBooks = int(books_purchased.get('Libros_comprados'))
            purchasedBooks += amount # we get all the purchased books
            cursor.execute("""SELECT total FROM Compras WHERE id_usuario = %s  """, (userID))
            TOTAL = cursor.fetchone()
            x = TOTAL.get('precio')
            total = book_price + amount*(int(price.get('precio'))) 
            cursor.execute ("""UPDATE Compras SET Libros_comprados=%s,total=%s WHERE id_usuario=%s""", (purchasedBooks,total,userID))


        #add one purchase to the user
        cursor.execute("""SELECT Libros_comprados FROM Usuarios WHERE correo = %s  """, (user_acount))
        value = cursor.fetchone()

        if value.get('Libros_comprados') == None:
            x = amount
            cursor.execute ("""UPDATE Usuarios SET Libros_comprados = %s WHERE id_usuario=%s""", (x, userID))
        else:
            x = int(value.get('Libros_comprados'))
            x += amount
            cursor.execute ("""UPDATE Usuarios SET Libros_comprados = %s WHERE id_usuario=%s""", (x, userID))

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
    
    mail.send(msg)
    return view_index(False)
    

@app.route('/template_add_cart')
def template_add_cart():
    #get Items from the cart and send them to template_cart.html
    connection = get_db_connection()
    with connection.cursor() as cursor:

        #get nombre_libro, autor, imagen, precio 
        #get id_usuario
        
        user_acount = session.get('id_usuario')
        cursor.execute("""SELECT Libros.id_libro, Libros.nombre_libro, Libros.autor, Libros.imagen, Libros.descripcion, Items.cantidad, Items.id_item, Items.total, Costos.precio
                            FROM Libros
                            INNER JOIN Items
                            INNER JOIN Costos
                            ON Libros.id_libro = Items.id_libro AND
                            Libros.id_libro = Costos.id_libro
                            WHERE Items.id_usuario = %s""", (user_acount))
        value = cursor.fetchall()

        prices = 0
        for fila in value:
            prices = prices + fila['total']
            

        #lets defined if there are books or not
        if len(value) > 0:
            cart = True
        else:
            cart = False

        connection.commit()  # Commit changes to the database
    connection.close()

    return render_template('template_cart.html', cart = cart, total_price = prices, labels = load_labels())
    

@app.route('/add_cart', methods=['POST'])
def add_cart():
    #get id_libro
    INDICE = int(request.form['id_libro'])
    amount = int(request.form.get('NumeroCarrito'))

    print("Compras : ",amount)

    connection = get_db_connection()
    with connection.cursor() as cursor:
        #get id_usuario
        userID = session.get('id_usuario')

        #get id_precio
        cursor.execute("""SELECT id_precio, precio FROM Costos WHERE id_libro = %s  """, (INDICE))
        value2 = cursor.fetchone()
        priceID = value2.get('id_precio')
        precio = value2.get('precio')
        total = precio*amount

        #Validación que no permitirá que se agrega un nuevo registro si ya existe, solo actualizará el valor
        cursor.execute("SELECT * FROM Items WHERE id_libro = %s AND id_usuario = %s", (INDICE, int(userID)))
        value3 = cursor.fetchone()

        print("CONTEO:")
        print("VALLLLLOOOOOOOOR")
        print(value3)
        

        if value3 is not None:
            cantidad = int(value3.get('cantidad')) + amount
            totalPrecio = cantidad*precio
            cursor.execute ("""UPDATE Items SET cantidad = %s, total = %s  WHERE id_item=%s""", (cantidad, totalPrecio, value3.get('id_item')))
        else:
            #insert into Items
            cursor.execute('INSERT INTO Items (id_usuario,cantidad,id_libro,id_precio,total) VALUES (%s,%s,%s,%s,%s)',(userID,amount,INDICE,priceID,total))

        connection.commit()  # Commit changes to the database
    connection.close()

    return book_details()

@app.route('/buy_Items')
def buy_Items():
    connection = get_db_connection()
    with connection.cursor() as cursor:

        #get id_usuario
        user_acount = session.get('correo')      
        cursor.execute("""SELECT id_usuario FROM Usuarios WHERE correo = %s  """, (user_acount))
        value = cursor.fetchone()
        userID = value.get('id_usuario')
        #get id_Libros
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
        
        total = 0
        for x in range(0,len(booksIDS)):#                                                                                     Libros comprados              total a pagar por libro                usuario      id libro
            cursor.execute('INSERT INTO Compras (Libros_comprados, total, id_usuario, id_libro) VALUES (%s,%s,%s,%s)',(AmountPerBook[x][0]['cantidad'],(prices[x][0]['precio'])*(AmountPerBook[x][0]['cantidad']) ,userID, booksIDS[x]['id_libro']))
            total += (prices[x][0]['precio'])*(AmountPerBook[x][0]['cantidad'])

        #add purchases to the user
        cursor.execute("""SELECT Libros_comprados FROM Usuarios WHERE correo = %s  """, (user_acount))
        value = cursor.fetchone()
        if value.get('Libros_comprados') == None:
            z = 0
            for x in range(0,len(booksIDS)):
                z += AmountPerBook[x][0]['cantidad']
            cursor.execute ("""UPDATE Usuarios SET Libros_comprados = %s WHERE id_usuario=%s""", (z, userID))
        else:
            z = int(value.get('Libros_comprados'))
            z += AmountPerBook[x][0]['cantidad']
            cursor.execute ("""UPDATE Usuarios SET Libros_comprados = %s WHERE id_usuario=%s""", (z, userID))

        #delete records from Items
        for x in range(0,len(booksIDS)):
            cursor.execute("""DELETE  FROM Items WHERE id_libro = %s  """, (booksIDS[x]['id_libro']))

        #delete books stock 
        for x in range(0,len(booksIDS)):
            cursor.execute("""SELECT stock FROM Libros WHERE id_libro = %s  """, (booksIDS[x]['id_libro']))
            value = cursor.fetchone()
            new_stock = value['stock'] - AmountPerBook[x][0]['cantidad']
            cursor.execute ("""UPDATE Libros SET stock = %s WHERE id_libro=%s""", (new_stock, booksIDS[x]['id_libro']))

        nombre = session.get('nombre_usuario')

        connection.commit()  # Commit changes to the database
    connection.close()
    
    html_body = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f9;
                    color: #333;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                }}
                h1 {{
                    color: #4CAF50;
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 20px;
                    margin-top: 20px;
                    background-color: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    font-weight: bold;
                }}
                .footer {{
                    font-size: 12px;
                    text-align: center;
                    color: #777;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Thank You {nombre} for Your Purchases!</h1>
                <p>We are processing your order. Below are the details:</p>
                <ul>
                    <li><strong>Order Number:</strong> #123456</li>
                    <li><strong>Amount:</strong> ${total}</li>
                    <li><strong>Status:</strong> Pending</li>
                </ul>
                <a href="http://yourwebsite.com" class="button">View Order</a>
            </div>
            <div class="footer">
                <p>Thank you for shopping with us!</p>
                <p><small>If you did not make this purchase, please contact our support immediately.</small></p>
            </div>
        </body>
    </html>
    """

    mail = Mail(app)
    user_acount = session.get('correo')
    msg = Message(subject = 'Ticket de compra',
                    sender='20223tn080@utez.edu.mx',
                    recipients=[user_acount],
                    body="This is the plain text body",
                    html=html_body
                    )

    mail.send(msg)



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
        print('VALUES = ',values) # VALUES =  [{'id_libro': x}, {'id_libro': x}, {'id_libro':z}, {'id_libro':z}, {'id_libro':z} ]

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

        #send the times the user had purchased the book
        amount = []
        cursor.execute("""SELECT Libros_comprados FROM Compras""")
        values = cursor.fetchall()
        for x in range(0,len(values)):
            amount.append(int(values[x]['Libros_comprados'])) # amount = [12,13,14,...]
        print("AMOUNT LIST = ",amount)
    
    return render_template('template_purchases.html',labels = load_labels(), BOOKS = books, rango = rango, list_amount = amount) 


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

        print("LISTA DE LOS IDS DE Usuarios  == ",lista)
    
        if userID in lista: # the user had already voted
            cursor.execute ("""UPDATE Opiniones SET estrellas = %s, comentario = %s  WHERE id_libro=%s""", (rating, comentario, INDICE))
        else:
            cursor.execute('INSERT INTO Opiniones (estrellas, id_libro, id_usuario, comentario) VALUES (%s,%s,%s,%s)',(rating ,INDICE, userID, comentario))

        print("COMENTARIOS ",comentario)

        connection.commit()  # Commit changes to the database
    connection.close()



    return template_purchases()


@app.route('/mostrarCarrito', methods=['POST'])
def mostrarCarrito():
    connection = get_db_connection()
    with connection.cursor() as cursor:

        #get nombre_libro, autor, imagen, precio 
        #get id_usuario
        user_acount = session.get('id_usuario')
        cursor.execute("""SELECT Libros.id_libro, Libros.nombre_libro, Libros.autor, Libros.imagen, Libros.descripcion, Items.cantidad, Items.id_item, Items.total, Costos.precio
                            FROM Libros
                            INNER JOIN Items
                            INNER JOIN Costos
                            ON Libros.id_libro = Items.id_libro AND
                            Libros.id_libro = Costos.id_libro
                            WHERE Items.id_usuario = %s""", (user_acount))
        value = cursor.fetchall()
        #Convertir los datos a formato que se serialice a JSON
        datos = []
        for fila in value:
            #eliminar = '<form method="post" id="formEliminar'+str(fila['id_item'])+'" action="../app/desktop/carrito.php"><a href="#" style="color: #cecece;" onclick="document.getElementById("formEliminar'+str(fila['id_item'])+'").submit()"><i class="fas fa-trash-alt"></i></a><input type="hidden" name="accion" value="eliminarCarritoResp"><input type="hidden" name="id_carrito" value="'+str(fila['id_item'])+'"></form>'
            eliminar = '<a href="#" style="color: #cecece;" onclick="eliminarRegCarrito('+str(fila['id_item'])+')"><i class="fas fa-trash-alt"></i></a>'

            imagen = "<div class=''><img src='"+fila['imagen']+"' class='img-fluid rounded-3' alt='Shopping item' style='width: 65px;'></div>"
            #total = fila['cantidad']*fila['precio']
            datos.append({
                'libro': imagen,
                'nombre': fila['nombre_libro'],
                'autor': fila['autor'],
                'descripcion': fila['descripcion'],
                'cantidad': fila['cantidad'],
                'precio': "$"+str(fila['precio']),
                'total': "$"+str(fila['total']),
                'eliminar': eliminar

            })

    connection.close()
    return jsonify(datos)

@app.route('/eliminarRegCarrito', methods=['POST'])
def eliminarRegCarrito():
    data = request.get_json()
    id_item = data['id_item']

    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("""DELETE FROM Items WHERE id_item = %s  """, (id_item))
        connection.commit()
        connection.close()

    return jsonify({'mensaje': 'Registro Eliminado'})


#this function is used with the paypal button
@app.route('/comprarLibro', methods=['POST'])
def comprarLibro():

    print("GOKUUUUUUUUUUUUUUUUUUUUUUUU")
    data = request.get_json()
    print(data['precio'])
    id_usuario = session.get('id_usuario')

    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("""SELECT precio, stock
                            FROM Libros
                            INNER JOIN Costos ON
                            Libros.id_libro = Costos.id_libro
                            WHERE Costos.id_libro = %s""", (data['id_libro']))
        #cursor.execute("""SELECT precio FROM Costos WHERE id_libro = %s  """, (data['id_libro']))
        value = cursor.fetchone()
        precio = value.get('precio')
        cant = int(data['cantidad'])
        total = cant*precio

        cursor.execute('INSERT INTO Compras (Libros_comprados,total,id_usuario,id_libro) VALUES (%s,%s,%s,%s)',(data['cantidad'],total,id_usuario,data['id_libro']))

        nuevoStock = value.get('stock')-cant

        print("CANTIDADDD: ",cant)
        print("PRECIOOOOOOO: ", precio)
        print("NUEVOSTOCK: ", nuevoStock)
        print("ID_LIBROOO: ", data['id_libro'])  
        cursor.execute ("""UPDATE Libros SET stock = %s WHERE id_libro=%s""", (nuevoStock, data['id_libro']))

        nombre = session.get('nombre_usuario')

        connection.commit()
    connection.close()

    #mail code
    # HTML email body with inline CSS for a nice design
    html_body = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f9;
                    color: #333;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                }}
                h1 {{
                    color: #4CAF50;
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 20px;
                    margin-top: 20px;
                    background-color: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    font-weight: bold;
                }}
                .footer {{
                    font-size: 12px;
                    text-align: center;
                    color: #777;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Thank You {nombre} for Your Purchase!</h1>
                <p>We are processing your order. Below are the details:</p>
                <ul>
                    <li><strong>Order Number:</strong> #123456</li>
                    <li><strong>Amount:</strong> ${total}</li>
                    <li><strong>Status:</strong> Pending</li>
                </ul>
                <a href="http://yourwebsite.com" class="button">View Order</a>
            </div>
            <div class="footer">
                <p>Thank you for shopping with us!</p>
                <p><small>If you did not make this purchase, please contact our support immediately.</small></p>
            </div>
        </body>
    </html>
    """

    mail = Mail(app)
    user_acount = session.get('correo')
    msg = Message(subject = 'Ticket de compra',
                    sender='20223tn080@utez.edu.mx',
                    recipients=[user_acount],
                    body="This is the plain text body",
                    html=html_body
                    )

    mail.send(msg)
    return jsonify({'mensaje': 'Compra exitosa'})


@app.route('/admin_libro')
def admin_libro():
    id_usuario = session.get('id_usuario')
    nombre = session.get('nombre_usuario')
    apellido = session.get('apellido_usuario')

    nombre_completo = nombre+" "+apellido

    return render_template('admin_book.html', nombre = nombre_completo)

@app.route('/mostrarLibroAdmin', methods=['POST'])
def mostrarLibroAdmin():
    connection = get_db_connection()
    with connection.cursor() as cursor:

        #get nombre_libro, autor, imagen, precio 
        #get id_usuario
        user_acount = session.get('id_usuario')
        cursor.execute("""SELECT Libros.id_libro, Libros.nombre_libro, Libros.autor, Libros.editorial, Libros.stock, Libros.descripcion, Costos.precio
                            FROM Libros 
                            INNER JOIN Costos ON 
                            Libros.id_libro = Costos.id_libro""")
        value = cursor.fetchall()
        #Convertir los datos a formato que se serialice a JSON
        datos = []
        for fila in value:
            eliminar = '<form action="/delete_book" method="POST" enctype="multipart/form-data"><input type="hidden" name="id_libro" value="'+str(fila['id_libro'])+'"><button type="submit"><i class="fas fa-trash-alt"></i></button></form>'
            #eliminar = '<a href="#" style="color: #cecece;" onclick="eliminarRegCarrito('+str(fila['id_libro'])+')"><i class="fas fa-trash-alt"></i></a>'
            editar = '<form action="/templates_edit_book" method="POST" enctype="multipart/form-data"><input type="hidden" name="id_libro" value="'+str(fila['id_libro'])+'"><button type="submit"><i class="fa-solid fa-pen-to-square"></i></button></form>'
            #editar = '<button type="button" onclick="editarLibro('+str(fila['id_libro'])+');"><i class="fa-solid fa-pen-to-square"></i></button>'
            datos.append({
                'nombre': fila['nombre_libro'],
                'autor': fila['autor'],
                'descripcion': fila['descripcion'],
                'editorial': fila['editorial'],
                'cantidad': fila['stock'],
                'precio': "$"+str(fila['precio']),
                'editar': editar,
                'eliminar': eliminar
            })

    connection.close()
    print(datos)
    return jsonify(datos)

#@app.route('/admin')
#def prueba():
#    return view_index_admin()

if __name__ == '__main__':
    app.run(debug=True)

#CODE TO GENERATE SECURE KEYS

#secretkey = binascii.hexlify(os.urandom(24)).decode()
