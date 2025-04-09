CREATE DATABASE libreria;

USE Libreria;

CREATE TABLE Usuarios (
			id_usuario INT AUTO_INCREMENT PRIMARY KEY,
			tipo_usuario BOOLEAN,
			nombre VARCHAR(50),
			apellido VARCHAR(50),
			nombre_usuario VARCHAR(50),
			direccion VARCHAR(150),
			teléfono VARCHAR(50),
			correo VARCHAR(50) UNIQUE,
			contraseña VARCHAR(50),
			libros_comprados INT

);
 
CREATE TABLE Compras(
			id_compra INT AUTO_INCREMENT PRIMARY KEY,
			libros_comprados VARCHAR(50),
			total DOUBLE
);

CREATE TABLE Costos(
			id_precio INT AUTO_INCREMENT PRIMARY KEY
);

CREATE TABLE Libros(
			id_libro INT AUTO_INCREMENT PRIMARY KEY,
			nombre_libro VARCHAR(50),
			autor VARCHAR(50),
			editorial VARCHAR(50),
			stock INT,
            imagen VARCHAR(50),
            descripcion VARCHAR(50)
);

CREATE TABLE Estado_libros(
			id_estado INT AUTO_INCREMENT PRIMARY KEY,
			disponible BOOLEAN,
			no_disponible BOOLEAN
);

CREATE TABLE Opiniones(
			id_opinion INT AUTO_INCREMENT PRIMARY KEY,
            estrellas INT,
            comentario VARCHAR(50)
);

CREATE TABLE Items(
			id_item INT AUTO_INCREMENT PRIMARY KEY,
            cantidad INT
);

SHOW TABLES;

-- Se crean las columnas que tendran las llaves foraneas y se vinculan las llaves foraneas 

ALTER TABLE Compras
ADD COLUMN id_usuario INT;

ALTER TABLE Compras
ADD CONSTRAINT fk_Compras_usuario FOREIGN KEY (id_usuario)
REFERENCES Usuarios (id_usuario);

ALTER TABLE Compras
ADD COLUMN id_libro INT;

ALTER TABLE Compras
ADD CONSTRAINT fk_Compras_Libro FOREIGN KEY (id_libro)
REFERENCES Libros (id_libro);

ALTER TABLE Costos
ADD COLUMN id_libro INT;

ALTER TABLE Costos
ADD CONSTRAINT fk_Costos_Libro FOREIGN KEY (id_libro)
REFERENCES Libros (id_libro)
ON DELETE CASCADE;

ALTER TABLE Libros
ADD COLUMN id_precio INT;

ALTER TABLE Libros
ADD CONSTRAINT fk_Libros_Precio FOREIGN KEY (id_precio)
REFERENCES Costos (id_precio)
ON DELETE CASCADE;

ALTER TABLE Estado_libros
ADD COLUMN id_libro INT;

ALTER TABLE Estado_libros
ADD CONSTRAINT fk_Estadolibros_Libro FOREIGN KEY (id_libro)
REFERENCES Libros (id_libro);


ALTER TABLE Opiniones 
ADD COLUMN id_libro INT;

ALTER TABLE Opiniones 
ADD COLUMN id_usuario INT;

ALTER TABLE Opiniones
ADD CONSTRAINT fk_Opiniones_Libro FOREIGN KEY (id_libro)
REFERENCES Libros (id_libro);

ALTER TABLE Opiniones
ADD CONSTRAINT fk_Opiniones_Usuario FOREIGN KEY (id_usuario)
REFERENCES Usuarios (id_usuario);

ALTER TABLE Libros
ADD COLUMN id_opinion INT;

ALTER TABLE Libros
ADD CONSTRAINT fk_Libros_Opinion FOREIGN KEY (id_opinion)
REFERENCES Opiniones (id_opinion);

ALTER TABLE Usuarios 
ADD COLUMN id_opinion INT;

ALTER TABLE Usuarios
ADD CONSTRAINT fk_Usuarios_Opinion FOREIGN KEY (id_opinion)
REFERENCES Opiniones (id_opinion);

-- new lines ------------------
ALTER TABLE Items
ADD COLUMN id_usuario INT;

ALTER TABLE Items
ADD CONSTRAINT fk_Items_Usuario FOREIGN KEY (id_usuario)
REFERENCES Usuarios (id_usuario);

ALTER TABLE Items
ADD COLUMN id_libro INT;

ALTER TABLE Items
ADD CONSTRAINT fk_Items_Libro FOREIGN KEY (id_libro)
REFERENCES Libros (id_libro);

ALTER TABLE Items
ADD COLUMN id_precio INT;

ALTER TABLE Items
ADD COLUMN total INT;

ALTER TABLE Items
ADD CONSTRAINT fk_Items_Precio FOREIGN KEY (id_precio)
REFERENCES Costos (id_precio);

-- end new lines ------------------




ALTER TABLE Costos
ADD COLUMN precio DOUBLE;

