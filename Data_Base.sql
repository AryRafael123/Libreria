SELECT * FROM Usuarios;

Drop database Librería;

DELETE FROM Usuarios WHERE id_usuario = 1;
DELETE FROM Usuarios WHERE id_usuario = 2;
DELETE FROM Usuarios WHERE id_usuario = 3;

-- usuario administrador
insert into Usuarios (tipo_usuario, nombre, apellido, nombre_usuario, direccion, teléfono, correo, contraseña)
values (True, "Ary Rafael", "Sánchez Hernández", "Ary123", "Morelos", "7775955444", "20223tn078@utez.edu.mx", "ary12345") ;

-- usuario normal 
insert into Usuarios (tipo_usuario, nombre, apellido, nombre_usuario, direccion, teléfono, correo, contraseña)
values (False, "Jose Emiliano", "Zuñiga Hernández", "Emi123", "Morelos", "777123456", "20223tn117@utez.edu.mx", "emi12345");

