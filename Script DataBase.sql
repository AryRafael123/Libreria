SELECT * FROM Libros;
SELECT * FROM Costos;
SELECT * FROM Usuarios;
SELECT * FROM Opiniones;

Drop database libreria;

DELETE FROM Costos where id_libro = 1;
DELETE FROM Libros where id_libro = 1;



-- usuario administrador
insert into Usuarios (tipo_usuario, nombre, apellido, nombre_usuario, direccion, teléfono, correo, contraseña)
values (True, "Ary Rafael", "Sánchez Hernández", "Ary123", "Morelos", "7775955444", "20223tn078@utez.edu.mx", "ary12345") ;

-- usuario normal 
insert into Usuarios (tipo_usuario, nombre, apellido, nombre_usuario, direccion, teléfono, correo, contraseña)
values (False, "Jose Emiliano", "Zuñiga Hernández", "Emi123", "Morelos", "777123456", "20223tn117@utez.edu.mx", "emi12345");

