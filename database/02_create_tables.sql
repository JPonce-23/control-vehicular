-- ============================================
-- Sistema de Control Vehicular
-- Script de creación de tablas
-- Base de datos: control_vehicular
-- ============================================


-- ============================================
-- TIPOS ENUM
-- ============================================

CREATE TYPE rol_usuario AS ENUM ('administrador','capturista');

CREATE TYPE estado_usuario AS ENUM ('activo', 'suspendido');


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
--Tabla: SALIDA
-- Registro de salidas de vehículos
-- ============================================

CREATE TYPE tipo_movimiento AS ENUM ('asignacion', 'devolucion');
CREATE TYPE forma_movimiento AS ENUM ('permanente', 'provisional');
CREATE TYPE nivel_gasolina_salida AS ENUM ('vacio', 'cuarto', 'medio', 'tres_cuartos', 'lleno');
CREATE TYPE estado_llantas_salida AS ENUM ('cuarto', 'medio', 'tres_cuartos', 'lleno');

CREATE TABLE salida (
    id SERIAL PRIMARY KEY,
    vehiculo_id INT NOT NULL REFERENCES vehiculo(id),
    persona_id INT NOT NULL REFERENCES persona_autorizada(id),
    capturado_por INT NOT NULL REFERENCES usuario_sistema(id),
    fecha_salida TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    num_oficio VARCHAR(100),
    num_expediente VARCHAR(100),
    cargo_en_viaje VARCHAR(100) NOT NULL,
    area_en_viaje VARCHAR(100) NOT NULL,
    tipo_movimiento tipo_movimiento NOT NULL,
    forma_movimiento forma_movimiento NOT NULL,
    fecha_fin_provisional DATE,
    finalidad_uso TEXT NOT NULL,
    km_odometro_salida DECIMAL(10, 2) NOT NULL,
    nivel_gasolina_salida nivel_gasolina_salida NOT NULL,
    estado_llantas_salida estado_llantas_salida NOT NULL,
    observaciones TEXT,
    observaciones_croquis TEXT
);

--=============================================
--Tabla: REGRESO
--Registro de regresos de vehículos
--=============================================

CREATE TYPE estado_vehiculo_regreso AS ENUM ('bueno', 'dañado', 'mantenimiento');
CREATE TYPE finalidad_devolucion AS ENUM ('disponible', 'reparacion', 'sustitucion');

CREATE TABLE regreso (
    id SERIAL PRIMARY KEY,
    salida_id INT NOT NULL REFERENCES salida(id),
    capturado_por INT NOT NULL REFERENCES usuario_sistema(id),
    fecha_regreso TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    km_odometro_regreso DECIMAL(10, 2) NOT NULL,
    nivel_gasolina_regreso  nivel_gasolina_salida  NOT NULL,
    estado_llantas_regreso  estado_llantas_salida  NOT NULL,
    estado_vehiculo_regreso estado_vehiculo_regreso NOT NULL,
    finalidad_devolucion finalidad_devolucion NOT NULL,
    observaciones TEXT
);

-- ============================================
-- Tabla: HISTORIAL_SALIDA
-- Para llevar un historial registrado de todas las salidas 
-- ============================================

CREATE TYPE accion AS ENUM ('registro_salida', 'registro_regreso', 'modificacion', 'generacion_resguardo');

CREATE TABLE historial_salida (
    id SERIAL PRIMARY KEY,
    salida_id INT NOT NULL REFERENCES salida(id),
    usuario_id INT NOT NULL REFERENCES usuario_sistema(id),
    accion accion NOT NULL,
    descripcion TEXT,
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

--============================================
-- Tabla: ITEM_INVENTARIO
-- Para llevar un registro de los items de checklist e inventario
--=============================================

CREATE TYPE categoria AS ENUM ('pieza', 'equipo_especial');
CREATE TYPE estado_default AS ENUM ('correcto', 'na');

CREATE TABLE item_inventario (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    categoria categoria NOT NULL,
    estado_default estado_default NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

--============================================
-- Tabla: REVISION_INVENTARIO
-- Para registrar las revisiones de checklist e inventario
--=============================================

CREATE TYPE estado_revision_inventario AS ENUM ('correcto', 'na', 'vacio');

CREATE TABLE revision_inventario (
    id SERIAL PRIMARY KEY,
    salida_id INT NOT NULL REFERENCES salida(id),
    item_id INT NOT NULL REFERENCES item_inventario(id),
    estado estado_revision_inventario NOT NULL,
    observaciones TEXT
);

--============================================
-- Tabla ITEM_CONDICION
-- Catálogo predeterminado de condiciones
--============================================

CREATE TYPE estado_condicion AS ENUM ('bueno', 'regular', 'malo');

CREATE TABLE item_condicion (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    estado_default estado_condicion NOT NULL DEFAULT 'bueno',
    activo BOOLEAN NOT NULL DEFAULT TRUE
);


--=============================================
-- Tabla REVISION_CONDICION
--Guarda el resultado de revisar cada condición de funcionalidad en una salida.
--=============================================

CREATE TABLE revision_condicion (
    id SERIAL PRIMARY KEY,
    salida_id INT NOT NULL REFERENCES salida(id),
    item_condicion_id INT NOT NULL REFERENCES item_condicion(id),
    estado estado_condicion NOT NULL,
    observaciones TEXT
);

--=============================================
--Tabla PRESUPUESTO_GASOLINA
--Guarda el presupuesto autorizado de gasolina para cada vehículo por año.
--=============================================

CREATE TABLE presupuesto_gasolina (
    id SERIAL PRIMARY KEY,
    vehiculo_id INT NOT NULL REFERENCES vehiculo(id),
    monto_autorizado_total DECIMAL (10,2) NOT NULL,
    monto_por_mes DECIMAL (10,2) NOT NULL,
    monto_utilizado DECIMAL (10,2) NOT NULL DEFAULT 0,
    saldo_acumulado DECIMAL (10,2) NOT NULL DEFAULT 0, 
    anio INT NOT NULL
);

--=============================================
--Tabla  GASTO_GASOLINA
--Registra los gastos de gasolina asociados a un vehículo, salida y presupuesto.
--=============================================

CREATE TABLE gasto_gasolina (
    id SERIAL PRIMARY KEY,
    vehiculo_id INT NOT NULL REFERENCES vehiculo(id),
    salida_id INT REFERENCES salida(id),
    presupuesto_id INT NOT NULL REFERENCES presupuesto_gasolina(id),
    fecha_gasto DATE NOT NULL,
    litros DECIMAL(10,2) NOT NULL,
    monto DECIMAL (10,2) NOT NULL,
    nota TEXT
); 

--=============================================
--Tabla AJUSTE_ODOMETRO
--Guarda correcciones o ajustes manuales del odómetro de un vehículo
--=============================================

CREATE TABLE ajuste_odometro (
    id SERIAL PRIMARY KEY,
    vehiculo_id INT NOT NULL REFERENCES vehiculo(id),
    fecha_ajuste TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    km_anterior DECIMAL (10,2) NOT NULL,
    km_nuevo DECIMAL (10,2) NOT NULL,
    motivo TEXT,
    realizado_por INT NOT NULL REFERENCES usuario_sistema(id)
);

--============================================
--Tabla RESGUARDO
--Guarda el archivo generado del resguardo listo para imprimir y firmar
--============================================

CREATE TABLE resguardo (
    id SERIAL PRIMARY KEY,
    salida_id INT NOT NULL REFERENCES salida(id),
    fecha_generacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    nombre_archivo VARCHAR(150) NOT NULL,
    ruta_archivo TEXT
);


-- ============================================
-- ORDEN DE CREACIÓN DE TABLAS
--USUARIO_SISTEMA
--TOKEN_ACCESO
--PERSONA_AUTORIZADA
--VEHICULO
--SALIDA
--REGRESO
--HISTORIAL_SALIDA
--Tablas de checklist/inventario
    --ITEM_INVENTARIO
    --REVISION_INVETARIO
    --ITEM_CONDICON
    --REVISION_CONDICION
--PRESUPUESTO_GASOLINA
--GASTO_GASOLINA
--AJUSTE_ODOMETRO
--RESGUARDO

