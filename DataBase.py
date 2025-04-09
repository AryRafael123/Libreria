import mysql.connector

mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="",
  database="librería"
)

mycursor = mydb.cursor()



sql = "INSERT INTO Usuarios (id_usuario, tipo_usuario, nombre, apellido, direccion, teléfono, correo, libros_comprados) VALUES (%s, %s, %s, %s,%s, %s,%s, %s)"

val = (2, True, "Ary", "Sanchez", "Cuernavaca Morelos", "77712345", "ary@gmail.com", 5)
mycursor.execute(sql,val)

mydb.commit()

print(mycursor.rowcount, "record inserted.")


