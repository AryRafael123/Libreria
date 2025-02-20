from flask import Flask, render_template, request, redirect, url_for
import pymysql

app = Flask(__name__)

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
def login():
    return render_template('index.html')
      


@app.route('/add_user', methods=['POST'])
def add_user():

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




if __name__ == '__main__':
    app.run(debug=True)
