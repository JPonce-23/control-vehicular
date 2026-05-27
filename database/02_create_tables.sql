-- ============================================
-- Sistema de Control Vehicular
-- Script de creación de tablas
-- Base de datos: control_vehicular
-- ============================================


-- ============================================
-- TIPOS ENUM
-- ============================================

CREATE TYPE rol_usuario AS ENUM (
    'administrador',
    'capturista'
);

CREATE TYPE estado_usuario AS ENUM (
    'activo',
    'suspendido'
);


-- ============================================
-- TABLAS
-- ============================================


-- ============================================
-- Tabla: USUARIO_SISTEMA
-- Personas que pueden iniciar sesión
-- ============================================

CREATE TABLE usuario_sistema (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100),
    num_empleado VARCHAR(50) NOT NULL UNIQUE,
    correo VARCHAR(150) NOT NULL UNIQUE,
    contrasena_hash VARCHAR(255) NOT NULL,
    rol rol_usuario NOT NULL,
    estado estado_usuario NOT NULL DEFAULT 'activo',
    fecha_alta TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP
);

-- ============================================
-- Tabla: TOKEN_ACCESO
-- Para registro de nuevos usuarios y recuperación de contraseñas
-- ============================================

CREATE TYPE tipo_token AS ENUM ('registro', 'recuperacion');

CREATE TABLE token_acceso (
	id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL REFERENCES usuario_sistema(id),
    token VARCHAR(64) NOT NULL UNIQUE,
    tipo tipo_token NOT NULL,
	fecha_expiracion TIMESTAMP NOT NULL,
    usado BOOLEAN NOT NULL DEFAULT FALSE
);

--============================================
-- Tabla: PERSONA_AUTORIZADA
-- Personas autorizadas a conducir vehículos oficiales
--============================================

CREATE TYPE estado_persona_autorizada AS ENUM ('activo', 'suspendido');

CREATE TABLE persona_autorizada (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100),
    num_licencia VARCHAR(25) NOT NULL UNIQUE,
    rfc VARCHAR(13) UNIQUE,
    vigencia_licencia DATE NOT NULL,
    tipo_licencia VARCHAR(50) NOT NULL,
    estado estado_persona_autorizada NOT NULL DEFAULT 'activo'
);

-- =============================================
-- Tabla: VEHICULO
-- Información de los vehículos oficiales
-- =============================================

CREATE TYPE estado_vehiculo AS ENUM ('disponible', 'en_uso', 'mantenimiento', 'fuera_de_servicio');

CREATE TABLE vehiculo (
    id SERIAL PRIMARY KEY,
    num_economico VARCHAR(50) NOT NULL UNIQUE,  
    placa VARCHAR(20) NOT NULL UNIQUE,
    marca VARCHAR(50) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    modelo_anio INT NOT NULL,
    cilindros INT NOT NULL,
    num_serie VARCHAR(50) NOT NULL UNIQUE,
    num_motor VARCHAR(50) UNIQUE,
    num_poliza VARCHAR(50),
    num_inventario VARCHAR(50) UNIQUE,
    color VARCHAR(30) NOT NULL,
    num_tarjeta_gasolina VARCHAR(50),
    km_acumulado DECIMAL(10, 2) NOT NULL DEFAULT 0,
    estado estado_vehiculo NOT NULL DEFAULT 'disponible'
);

-- ============================================
-- ORDEN DE CREACIÓN DE TABLAS
--USUARIO_SISTEMA
--TOKEN_ACCESO
--PERSONA_AUTORIZADA
--VEHICULO
SALIDA
REGRESO
HISTORIAL_SALIDA
Tablas de checklist/inventario
Presupuesto/gasto gasolina
Ajuste odómetro
Resguardo

