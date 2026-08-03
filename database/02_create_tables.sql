-- Instalación limpia del Sistema de Control Vehicular.
-- Ejecutar sobre una base de datos VACÍA.

CREATE TYPE rol_usuario AS ENUM ('administrador', 'capturista');
CREATE TYPE estado_usuario AS ENUM ('activo', 'suspendido');
CREATE TYPE tipo_token AS ENUM ('registro', 'recuperacion');
CREATE TYPE estado_persona_autorizada AS ENUM ('activo', 'suspendido');
CREATE TYPE estado_vehiculo AS ENUM ('disponible', 'en_uso', 'mantenimiento', 'fuera_de_servicio');
CREATE TYPE tipo_movimiento AS ENUM ('asignacion', 'devolucion');
CREATE TYPE forma_movimiento AS ENUM ('permanente', 'provisional');
CREATE TYPE nivel_gasolina_salida AS ENUM ('vacio', 'cuarto', 'medio', 'tres_cuartos', 'lleno');
CREATE TYPE estado_llantas_salida AS ENUM ('cuarto', 'medio', 'tres_cuartos', 'lleno');
CREATE TYPE estado_vehiculo_regreso AS ENUM ('bueno', 'dañado', 'mantenimiento');
CREATE TYPE finalidad_devolucion AS ENUM ('disponible', 'reparacion', 'sustitucion');
CREATE TYPE accion AS ENUM ('registro_salida', 'registro_regreso', 'modificacion', 'generacion_resguardo');
CREATE TYPE categoria AS ENUM ('pieza', 'equipo_especial');
CREATE TYPE estado_default AS ENUM ('correcto', 'na');
CREATE TYPE estado_revision_inventario AS ENUM ('correcto', 'na', 'vacio');
CREATE TYPE estado_condicion AS ENUM ('bueno', 'regular', 'malo');

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
    es_superadmin BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_alta TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP
);

CREATE UNIQUE INDEX ux_usuario_superadmin_unico
ON usuario_sistema (es_superadmin)
WHERE es_superadmin = TRUE;

CREATE TABLE token_acceso (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL REFERENCES usuario_sistema(id) ON DELETE CASCADE,
    token VARCHAR(128) NOT NULL UNIQUE,
    tipo tipo_token NOT NULL,
    fecha_expiracion TIMESTAMP NOT NULL,
    usado BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE persona_autorizada (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100),
    cargo VARCHAR(150) NOT NULL,
    num_licencia VARCHAR(25) UNIQUE,
    rfc VARCHAR(13) UNIQUE,
    vigencia_licencia DATE,
    tipo_licencia VARCHAR(50),
    estado estado_persona_autorizada NOT NULL DEFAULT 'activo'
);

CREATE TABLE vehiculo (
    id SERIAL PRIMARY KEY,
    num_economico VARCHAR(50) UNIQUE,
    placa VARCHAR(20) NOT NULL UNIQUE,
    marca VARCHAR(50) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    modelo_anio INT NOT NULL CHECK (modelo_anio >= 1900),
    cilindros INT NOT NULL CHECK (cilindros > 0),
    num_serie VARCHAR(50) NOT NULL UNIQUE,
    num_motor VARCHAR(50) UNIQUE,
    num_poliza VARCHAR(50),
    num_inventario VARCHAR(50) UNIQUE,
    color VARCHAR(30) NOT NULL,
    num_tarjeta_gasolina VARCHAR(50),
    saldo_tarjeta_gasolina DECIMAL(12, 2) NOT NULL DEFAULT 0 CHECK (saldo_tarjeta_gasolina >= 0),
    km_acumulado DECIMAL(12, 2) NOT NULL DEFAULT 0 CHECK (km_acumulado >= 0),
    estado estado_vehiculo NOT NULL DEFAULT 'disponible'
);

CREATE UNIQUE INDEX ux_vehiculo_tarjeta_gasolina
ON vehiculo (num_tarjeta_gasolina)
WHERE num_tarjeta_gasolina IS NOT NULL AND btrim(num_tarjeta_gasolina) <> '';

CREATE TABLE salida (
    id SERIAL PRIMARY KEY,
    vehiculo_id INT NOT NULL REFERENCES vehiculo(id),
    persona_id INT NOT NULL REFERENCES persona_autorizada(id),
    capturado_por INT NOT NULL REFERENCES usuario_sistema(id),
    fecha_salida TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    num_oficio VARCHAR(100),
    num_expediente VARCHAR(100),
    area_en_viaje VARCHAR(100),
    cargo_en_viaje VARCHAR(150),
    tipo_movimiento tipo_movimiento NOT NULL,
    forma_movimiento forma_movimiento NOT NULL DEFAULT 'provisional',
    fecha_fin_provisional DATE,
    fecha_regreso_estimada DATE,
    finalidad_uso TEXT NOT NULL,
    km_odometro_salida DECIMAL(12, 2) NOT NULL CHECK (km_odometro_salida >= 0),
    nivel_gasolina_salida nivel_gasolina_salida NOT NULL,
    estado_llantas_salida estado_llantas_salida NOT NULL,
    observaciones TEXT,
    observaciones_croquis TEXT,
    monto_agregado_tarjeta DECIMAL(12, 2) NOT NULL DEFAULT 0 CHECK (monto_agregado_tarjeta >= 0),
    saldo_tarjeta_salida DECIMAL(12, 2) NOT NULL DEFAULT 0 CHECK (saldo_tarjeta_salida >= 0)
);

CREATE TABLE regreso (
    id SERIAL PRIMARY KEY,
    salida_id INT NOT NULL UNIQUE REFERENCES salida(id),
    capturado_por INT NOT NULL REFERENCES usuario_sistema(id),
    fecha_regreso TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    km_odometro_regreso DECIMAL(12, 2) NOT NULL CHECK (km_odometro_regreso >= 0),
    nivel_gasolina_regreso nivel_gasolina_salida NOT NULL,
    estado_llantas_regreso estado_llantas_salida NOT NULL,
    estado_vehiculo_regreso estado_vehiculo_regreso NOT NULL,
    finalidad_devolucion finalidad_devolucion NOT NULL,
    saldo_tarjeta_antes_regreso DECIMAL(12, 2),
    saldo_tarjeta_regreso DECIMAL(12, 2),
    monto_gastado_tarjeta DECIMAL(12, 2),
    observaciones TEXT
);

CREATE TABLE historial_salida (
    id SERIAL PRIMARY KEY,
    salida_id INT NOT NULL REFERENCES salida(id),
    usuario_id INT NOT NULL REFERENCES usuario_sistema(id),
    accion accion NOT NULL,
    descripcion TEXT,
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE item_inventario (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    categoria categoria NOT NULL,
    estado_default estado_default NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE revision_inventario (
    id SERIAL PRIMARY KEY,
    salida_id INT NOT NULL REFERENCES salida(id) ON DELETE CASCADE,
    item_id INT NOT NULL REFERENCES item_inventario(id),
    estado estado_revision_inventario NOT NULL,
    observaciones TEXT,
    UNIQUE (salida_id, item_id)
);

CREATE TABLE item_condicion (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    estado_default estado_condicion NOT NULL DEFAULT 'bueno',
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE revision_condicion (
    id SERIAL PRIMARY KEY,
    salida_id INT NOT NULL REFERENCES salida(id) ON DELETE CASCADE,
    item_condicion_id INT NOT NULL REFERENCES item_condicion(id),
    estado estado_condicion NOT NULL,
    observaciones TEXT,
    UNIQUE (salida_id, item_condicion_id)
);

CREATE TABLE presupuesto_gasolina (
    id SERIAL PRIMARY KEY,
    vehiculo_id INT NOT NULL REFERENCES vehiculo(id),
    monto_autorizado_total DECIMAL(12, 2) NOT NULL CHECK (monto_autorizado_total > 0),
    monto_por_mes DECIMAL(12, 2) NOT NULL CHECK (monto_por_mes >= 0),
    monto_utilizado DECIMAL(12, 2) NOT NULL DEFAULT 0 CHECK (monto_utilizado >= 0),
    saldo_acumulado DECIMAL(12, 2) NOT NULL DEFAULT 0,
    anio INT NOT NULL CHECK (anio >= 2000),
    mes_inicio INT NOT NULL DEFAULT 1 CHECK (mes_inicio BETWEEN 1 AND 12),
    mes_fin INT NOT NULL DEFAULT 12 CHECK (mes_fin BETWEEN 1 AND 12),
    CONSTRAINT ck_presupuesto_rango_meses CHECK (mes_inicio <= mes_fin),
    CONSTRAINT presupuesto_gasolina_vehiculo_anio_unique UNIQUE (vehiculo_id, anio)
);

CREATE TABLE gasto_gasolina (
    id SERIAL PRIMARY KEY,
    vehiculo_id INT NOT NULL REFERENCES vehiculo(id),
    salida_id INT NOT NULL REFERENCES salida(id),
    presupuesto_id INT NOT NULL REFERENCES presupuesto_gasolina(id),
    fecha_gasto DATE NOT NULL,
    litros DECIMAL(10, 2),
    monto DECIMAL(12, 2) NOT NULL CHECK (monto > 0),
    nivel_tanque nivel_gasolina_salida,
    km_odometro DECIMAL(12, 2),
    nota TEXT,
    capturado_por INT NOT NULL REFERENCES usuario_sistema(id),
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ajuste_odometro (
    id SERIAL PRIMARY KEY,
    vehiculo_id INT NOT NULL REFERENCES vehiculo(id),
    fecha_ajuste TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    km_anterior DECIMAL(12, 2) NOT NULL,
    km_nuevo DECIMAL(12, 2) NOT NULL CHECK (km_nuevo >= 0),
    motivo TEXT,
    realizado_por INT NOT NULL REFERENCES usuario_sistema(id)
);

CREATE TABLE resguardo (
    id SERIAL PRIMARY KEY,
    salida_id INT NOT NULL UNIQUE REFERENCES salida(id),
    fecha_generacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    nombre_archivo VARCHAR(150) NOT NULL,
    ruta_archivo TEXT NOT NULL
);

CREATE INDEX idx_salida_vehiculo ON salida (vehiculo_id);
CREATE INDEX idx_salida_persona ON salida (persona_id);
CREATE INDEX idx_regreso_salida ON regreso (salida_id);
CREATE INDEX idx_historial_salida ON historial_salida (salida_id, fecha DESC);
CREATE INDEX idx_gasto_gasolina_vehiculo ON gasto_gasolina (vehiculo_id);
CREATE INDEX idx_gasto_gasolina_fecha ON gasto_gasolina (fecha_gasto);
CREATE INDEX idx_gasto_gasolina_presupuesto ON gasto_gasolina (presupuesto_id);
