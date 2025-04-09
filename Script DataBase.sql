SELECT * FROM Usuarios;
SELECT * FROM Libros;
SELECT * FROM Compras;
SELECT * FROM Costos;
SELECT * FROM Opiniones;
SELECT * FROM Items;


Drop database libreria;


-- usuario administrador
insert into Usuarios (tipo_usuario, nombre, apellido, nombre_usuario, direccion, teléfono, correo, contraseña)
values (True, "Ary", "Sanchez", "admin", "Morelos", "77711111111", "20223tn078@utez.edu.mx", "ary12345") ;

-- usuario normal 
insert into Usuarios (tipo_usuario, nombre, apellido, nombre_usuario, direccion, teléfono, correo, contraseña)
values (False, "Hassiel", "Soria", "cliente", "Morelos", "7772222222", "20223tn080@utez.edu.mx", "hassi12345");

