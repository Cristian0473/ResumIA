-- Eliminar las tablas si existen (en orden correcto para evitar conflictos de clave foránea)
DROP TABLE IF EXISTS usuarios CASCADE;
DROP TABLE IF EXISTS personas CASCADE;
DROP TABLE IF EXISTS roles CASCADE;

-- Crear tabla de roles
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    estado BOOLEAN DEFAULT TRUE
);

-- Crear tabla de personas (ya sin DNI)
CREATE TABLE personas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    imagen VARCHAR(255),
    id_rol INTEGER,
    FOREIGN KEY (id_rol) REFERENCES roles(id) ON UPDATE CASCADE ON DELETE SET NULL
);

-- Crear tabla de usuarios (correo es el identificador principal)
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    correo VARCHAR(100) NOT NULL UNIQUE,
    pass VARCHAR(255) NOT NULL,
    token VARCHAR(512),
    id_persona INTEGER,
    FOREIGN KEY (id_persona) REFERENCES personas(id) ON UPDATE NO ACTION ON DELETE NO ACTION
);



INSERT INTO roles (id, nombre, descripcion) VALUES
(1, 'Usuario', 'Rol básico con funciones limitadas como cargar textos y recibir resúmenes'),
(2, 'Visionario', 'Rol con enfoque estratégico e innovación'), 
(3, 'Administrativo', 'Rol administrativo operativo en la plataforma'),
(4, 'Hacker', 'Encargado del desarrollo y soporte técnico del sistema');