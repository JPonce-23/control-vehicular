--
-- PostgreSQL database dump
--

\restrict u7kRNCV5PAgb1iAxfcOYiiy6TO6gcTC1tO2R6RvztOBTDQXSxGnc55T2efBGZwj

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: accion; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.accion AS ENUM (
    'registro_salida',
    'registro_regreso',
    'modificacion',
    'generacion_resguardo'
);


ALTER TYPE public.accion OWNER TO postgres;

--
-- Name: categoria; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.categoria AS ENUM (
    'pieza',
    'equipo_especial'
);


ALTER TYPE public.categoria OWNER TO postgres;

--
-- Name: estado_condicion; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.estado_condicion AS ENUM (
    'bueno',
    'regular',
    'malo'
);


ALTER TYPE public.estado_condicion OWNER TO postgres;

--
-- Name: estado_default; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.estado_default AS ENUM (
    'correcto',
    'na'
);


ALTER TYPE public.estado_default OWNER TO postgres;

--
-- Name: estado_llantas_salida; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.estado_llantas_salida AS ENUM (
    'cuarto',
    'medio',
    'tres_cuartos',
    'lleno'
);


ALTER TYPE public.estado_llantas_salida OWNER TO postgres;

--
-- Name: estado_persona_autorizada; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.estado_persona_autorizada AS ENUM (
    'activo',
    'suspendido'
);


ALTER TYPE public.estado_persona_autorizada OWNER TO postgres;

--
-- Name: estado_revision_inventario; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.estado_revision_inventario AS ENUM (
    'correcto',
    'na',
    'vacio'
);


ALTER TYPE public.estado_revision_inventario OWNER TO postgres;

--
-- Name: estado_usuario; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.estado_usuario AS ENUM (
    'activo',
    'suspendido'
);


ALTER TYPE public.estado_usuario OWNER TO postgres;

--
-- Name: estado_vehiculo; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.estado_vehiculo AS ENUM (
    'disponible',
    'en_uso',
    'mantenimiento',
    'fuera_de_servicio'
);


ALTER TYPE public.estado_vehiculo OWNER TO postgres;

--
-- Name: estado_vehiculo_regreso; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.estado_vehiculo_regreso AS ENUM (
    'bueno',
    'dañado',
    'mantenimiento'
);


ALTER TYPE public.estado_vehiculo_regreso OWNER TO postgres;

--
-- Name: finalidad_devolucion; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.finalidad_devolucion AS ENUM (
    'disponible',
    'reparacion',
    'sustitucion'
);


ALTER TYPE public.finalidad_devolucion OWNER TO postgres;

--
-- Name: forma_movimiento; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.forma_movimiento AS ENUM (
    'permanente',
    'provisional'
);


ALTER TYPE public.forma_movimiento OWNER TO postgres;

--
-- Name: nivel_gasolina_salida; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.nivel_gasolina_salida AS ENUM (
    'vacio',
    'cuarto',
    'medio',
    'tres_cuartos',
    'lleno'
);


ALTER TYPE public.nivel_gasolina_salida OWNER TO postgres;

--
-- Name: rol_usuario; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.rol_usuario AS ENUM (
    'administrador',
    'capturista'
);


ALTER TYPE public.rol_usuario OWNER TO postgres;

--
-- Name: tipo_movimiento; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tipo_movimiento AS ENUM (
    'asignacion',
    'devolucion'
);


ALTER TYPE public.tipo_movimiento OWNER TO postgres;

--
-- Name: tipo_token; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tipo_token AS ENUM (
    'registro',
    'recuperacion'
);


ALTER TYPE public.tipo_token OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: ajuste_odometro; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ajuste_odometro (
    id integer NOT NULL,
    vehiculo_id integer NOT NULL,
    fecha_ajuste timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    km_anterior numeric(12,2) NOT NULL,
    km_nuevo numeric(12,2) NOT NULL,
    motivo text,
    realizado_por integer NOT NULL,
    CONSTRAINT ajuste_odometro_km_nuevo_check CHECK ((km_nuevo >= (0)::numeric))
);


ALTER TABLE public.ajuste_odometro OWNER TO postgres;

--
-- Name: ajuste_odometro_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ajuste_odometro_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ajuste_odometro_id_seq OWNER TO postgres;

--
-- Name: ajuste_odometro_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ajuste_odometro_id_seq OWNED BY public.ajuste_odometro.id;


--
-- Name: gasto_gasolina; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gasto_gasolina (
    id integer NOT NULL,
    vehiculo_id integer NOT NULL,
    salida_id integer NOT NULL,
    presupuesto_id integer NOT NULL,
    fecha_gasto date NOT NULL,
    litros numeric(10,2),
    monto numeric(12,2) NOT NULL,
    nivel_tanque public.nivel_gasolina_salida,
    km_odometro numeric(12,2),
    nota text,
    capturado_por integer NOT NULL,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT gasto_gasolina_monto_check CHECK ((monto > (0)::numeric))
);


ALTER TABLE public.gasto_gasolina OWNER TO postgres;

--
-- Name: gasto_gasolina_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.gasto_gasolina_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.gasto_gasolina_id_seq OWNER TO postgres;

--
-- Name: gasto_gasolina_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.gasto_gasolina_id_seq OWNED BY public.gasto_gasolina.id;


--
-- Name: historial_salida; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.historial_salida (
    id integer NOT NULL,
    salida_id integer NOT NULL,
    usuario_id integer NOT NULL,
    accion public.accion NOT NULL,
    descripcion text,
    fecha timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.historial_salida OWNER TO postgres;

--
-- Name: historial_salida_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.historial_salida_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.historial_salida_id_seq OWNER TO postgres;

--
-- Name: historial_salida_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.historial_salida_id_seq OWNED BY public.historial_salida.id;


--
-- Name: item_condicion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.item_condicion (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    estado_default public.estado_condicion DEFAULT 'bueno'::public.estado_condicion NOT NULL,
    activo boolean DEFAULT true NOT NULL
);


ALTER TABLE public.item_condicion OWNER TO postgres;

--
-- Name: item_condicion_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.item_condicion_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.item_condicion_id_seq OWNER TO postgres;

--
-- Name: item_condicion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.item_condicion_id_seq OWNED BY public.item_condicion.id;


--
-- Name: item_inventario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.item_inventario (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    categoria public.categoria NOT NULL,
    estado_default public.estado_default NOT NULL,
    activo boolean DEFAULT true NOT NULL
);


ALTER TABLE public.item_inventario OWNER TO postgres;

--
-- Name: item_inventario_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.item_inventario_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.item_inventario_id_seq OWNER TO postgres;

--
-- Name: item_inventario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.item_inventario_id_seq OWNED BY public.item_inventario.id;


--
-- Name: persona_autorizada; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.persona_autorizada (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    apellido_paterno character varying(100) NOT NULL,
    apellido_materno character varying(100),
    cargo character varying(150) NOT NULL,
    num_licencia character varying(25),
    rfc character varying(13),
    vigencia_licencia date,
    tipo_licencia character varying(50),
    estado public.estado_persona_autorizada DEFAULT 'activo'::public.estado_persona_autorizada NOT NULL
);


ALTER TABLE public.persona_autorizada OWNER TO postgres;

--
-- Name: persona_autorizada_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.persona_autorizada_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.persona_autorizada_id_seq OWNER TO postgres;

--
-- Name: persona_autorizada_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.persona_autorizada_id_seq OWNED BY public.persona_autorizada.id;


--
-- Name: presupuesto_gasolina; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.presupuesto_gasolina (
    id integer NOT NULL,
    vehiculo_id integer NOT NULL,
    monto_autorizado_total numeric(12,2) NOT NULL,
    monto_por_mes numeric(12,2) NOT NULL,
    monto_utilizado numeric(12,2) DEFAULT 0 NOT NULL,
    saldo_acumulado numeric(12,2) DEFAULT 0 NOT NULL,
    anio integer NOT NULL,
    mes_inicio integer DEFAULT 1 NOT NULL,
    mes_fin integer DEFAULT 12 NOT NULL,
    CONSTRAINT ck_presupuesto_rango_meses CHECK ((mes_inicio <= mes_fin)),
    CONSTRAINT presupuesto_gasolina_anio_check CHECK ((anio >= 2000)),
    CONSTRAINT presupuesto_gasolina_mes_fin_check CHECK (((mes_fin >= 1) AND (mes_fin <= 12))),
    CONSTRAINT presupuesto_gasolina_mes_inicio_check CHECK (((mes_inicio >= 1) AND (mes_inicio <= 12))),
    CONSTRAINT presupuesto_gasolina_monto_autorizado_total_check CHECK ((monto_autorizado_total > (0)::numeric)),
    CONSTRAINT presupuesto_gasolina_monto_por_mes_check CHECK ((monto_por_mes >= (0)::numeric)),
    CONSTRAINT presupuesto_gasolina_monto_utilizado_check CHECK ((monto_utilizado >= (0)::numeric))
);


ALTER TABLE public.presupuesto_gasolina OWNER TO postgres;

--
-- Name: presupuesto_gasolina_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.presupuesto_gasolina_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.presupuesto_gasolina_id_seq OWNER TO postgres;

--
-- Name: presupuesto_gasolina_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.presupuesto_gasolina_id_seq OWNED BY public.presupuesto_gasolina.id;


--
-- Name: regreso; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.regreso (
    id integer NOT NULL,
    salida_id integer NOT NULL,
    capturado_por integer NOT NULL,
    fecha_regreso timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    km_odometro_regreso numeric(12,2) NOT NULL,
    nivel_gasolina_regreso public.nivel_gasolina_salida NOT NULL,
    estado_llantas_regreso public.estado_llantas_salida NOT NULL,
    estado_vehiculo_regreso public.estado_vehiculo_regreso NOT NULL,
    finalidad_devolucion public.finalidad_devolucion NOT NULL,
    saldo_tarjeta_antes_regreso numeric(12,2),
    saldo_tarjeta_regreso numeric(12,2),
    monto_gastado_tarjeta numeric(12,2),
    observaciones text,
    CONSTRAINT regreso_km_odometro_regreso_check CHECK ((km_odometro_regreso >= (0)::numeric))
);


ALTER TABLE public.regreso OWNER TO postgres;

--
-- Name: regreso_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.regreso_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.regreso_id_seq OWNER TO postgres;

--
-- Name: regreso_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.regreso_id_seq OWNED BY public.regreso.id;


--
-- Name: resguardo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.resguardo (
    id integer NOT NULL,
    salida_id integer NOT NULL,
    fecha_generacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    nombre_archivo character varying(150) NOT NULL,
    ruta_archivo text NOT NULL
);


ALTER TABLE public.resguardo OWNER TO postgres;

--
-- Name: resguardo_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.resguardo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.resguardo_id_seq OWNER TO postgres;

--
-- Name: resguardo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.resguardo_id_seq OWNED BY public.resguardo.id;


--
-- Name: revision_condicion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.revision_condicion (
    id integer NOT NULL,
    salida_id integer NOT NULL,
    item_condicion_id integer NOT NULL,
    estado public.estado_condicion NOT NULL,
    observaciones text
);


ALTER TABLE public.revision_condicion OWNER TO postgres;

--
-- Name: revision_condicion_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.revision_condicion_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.revision_condicion_id_seq OWNER TO postgres;

--
-- Name: revision_condicion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.revision_condicion_id_seq OWNED BY public.revision_condicion.id;


--
-- Name: revision_inventario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.revision_inventario (
    id integer NOT NULL,
    salida_id integer NOT NULL,
    item_id integer NOT NULL,
    estado public.estado_revision_inventario NOT NULL,
    observaciones text
);


ALTER TABLE public.revision_inventario OWNER TO postgres;

--
-- Name: revision_inventario_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.revision_inventario_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.revision_inventario_id_seq OWNER TO postgres;

--
-- Name: revision_inventario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.revision_inventario_id_seq OWNED BY public.revision_inventario.id;


--
-- Name: salida; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.salida (
    id integer NOT NULL,
    vehiculo_id integer NOT NULL,
    persona_id integer NOT NULL,
    capturado_por integer NOT NULL,
    fecha_salida timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    num_oficio character varying(100),
    num_expediente character varying(100),
    area_en_viaje character varying(100),
    cargo_en_viaje character varying(150),
    tipo_movimiento public.tipo_movimiento NOT NULL,
    forma_movimiento public.forma_movimiento DEFAULT 'provisional'::public.forma_movimiento NOT NULL,
    fecha_fin_provisional date,
    fecha_regreso_estimada date,
    finalidad_uso text NOT NULL,
    km_odometro_salida numeric(12,2) NOT NULL,
    nivel_gasolina_salida public.nivel_gasolina_salida NOT NULL,
    estado_llantas_salida public.estado_llantas_salida NOT NULL,
    observaciones text,
    observaciones_croquis text,
    monto_agregado_tarjeta numeric(12,2) DEFAULT 0 NOT NULL,
    saldo_tarjeta_salida numeric(12,2) DEFAULT 0 NOT NULL,
    CONSTRAINT salida_km_odometro_salida_check CHECK ((km_odometro_salida >= (0)::numeric)),
    CONSTRAINT salida_monto_agregado_tarjeta_check CHECK ((monto_agregado_tarjeta >= (0)::numeric)),
    CONSTRAINT salida_saldo_tarjeta_salida_check CHECK ((saldo_tarjeta_salida >= (0)::numeric))
);


ALTER TABLE public.salida OWNER TO postgres;

--
-- Name: salida_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.salida_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.salida_id_seq OWNER TO postgres;

--
-- Name: salida_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.salida_id_seq OWNED BY public.salida.id;


--
-- Name: token_acceso; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.token_acceso (
    id integer NOT NULL,
    usuario_id integer NOT NULL,
    token character varying(128) NOT NULL,
    tipo public.tipo_token NOT NULL,
    fecha_expiracion timestamp without time zone NOT NULL,
    usado boolean DEFAULT false NOT NULL
);


ALTER TABLE public.token_acceso OWNER TO postgres;

--
-- Name: token_acceso_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.token_acceso_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.token_acceso_id_seq OWNER TO postgres;

--
-- Name: token_acceso_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.token_acceso_id_seq OWNED BY public.token_acceso.id;


--
-- Name: usuario_sistema; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuario_sistema (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    apellido_paterno character varying(100) NOT NULL,
    apellido_materno character varying(100),
    num_empleado character varying(50) NOT NULL,
    correo character varying(150) NOT NULL,
    contrasena_hash character varying(255) NOT NULL,
    rol public.rol_usuario NOT NULL,
    estado public.estado_usuario DEFAULT 'activo'::public.estado_usuario NOT NULL,
    es_superadmin boolean DEFAULT false NOT NULL,
    fecha_alta timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ultimo_acceso timestamp without time zone
);


ALTER TABLE public.usuario_sistema OWNER TO postgres;

--
-- Name: usuario_sistema_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuario_sistema_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuario_sistema_id_seq OWNER TO postgres;

--
-- Name: usuario_sistema_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuario_sistema_id_seq OWNED BY public.usuario_sistema.id;


--
-- Name: vehiculo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vehiculo (
    id integer NOT NULL,
    num_economico character varying(50),
    placa character varying(20) NOT NULL,
    marca character varying(50) NOT NULL,
    tipo character varying(50) NOT NULL,
    modelo_anio integer NOT NULL,
    cilindros integer NOT NULL,
    num_serie character varying(50) NOT NULL,
    num_motor character varying(50),
    num_poliza character varying(50),
    num_inventario character varying(50),
    color character varying(30) NOT NULL,
    num_tarjeta_gasolina character varying(50),
    saldo_tarjeta_gasolina numeric(12,2) DEFAULT 0 NOT NULL,
    km_acumulado integer DEFAULT 0 NOT NULL,
    estado public.estado_vehiculo DEFAULT 'disponible'::public.estado_vehiculo NOT NULL,
    CONSTRAINT vehiculo_cilindros_check CHECK ((cilindros > 0)),
    CONSTRAINT vehiculo_km_acumulado_check CHECK (((km_acumulado)::numeric >= (0)::numeric)),
    CONSTRAINT vehiculo_modelo_anio_check CHECK ((modelo_anio >= 1900)),
    CONSTRAINT vehiculo_saldo_tarjeta_gasolina_check CHECK ((saldo_tarjeta_gasolina >= (0)::numeric))
);


ALTER TABLE public.vehiculo OWNER TO postgres;

--
-- Name: vehiculo_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vehiculo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehiculo_id_seq OWNER TO postgres;

--
-- Name: vehiculo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vehiculo_id_seq OWNED BY public.vehiculo.id;


--
-- Name: ajuste_odometro id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ajuste_odometro ALTER COLUMN id SET DEFAULT nextval('public.ajuste_odometro_id_seq'::regclass);


--
-- Name: gasto_gasolina id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gasto_gasolina ALTER COLUMN id SET DEFAULT nextval('public.gasto_gasolina_id_seq'::regclass);


--
-- Name: historial_salida id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historial_salida ALTER COLUMN id SET DEFAULT nextval('public.historial_salida_id_seq'::regclass);


--
-- Name: item_condicion id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.item_condicion ALTER COLUMN id SET DEFAULT nextval('public.item_condicion_id_seq'::regclass);


--
-- Name: item_inventario id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.item_inventario ALTER COLUMN id SET DEFAULT nextval('public.item_inventario_id_seq'::regclass);


--
-- Name: persona_autorizada id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.persona_autorizada ALTER COLUMN id SET DEFAULT nextval('public.persona_autorizada_id_seq'::regclass);


--
-- Name: presupuesto_gasolina id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.presupuesto_gasolina ALTER COLUMN id SET DEFAULT nextval('public.presupuesto_gasolina_id_seq'::regclass);


--
-- Name: regreso id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.regreso ALTER COLUMN id SET DEFAULT nextval('public.regreso_id_seq'::regclass);


--
-- Name: resguardo id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resguardo ALTER COLUMN id SET DEFAULT nextval('public.resguardo_id_seq'::regclass);


--
-- Name: revision_condicion id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.revision_condicion ALTER COLUMN id SET DEFAULT nextval('public.revision_condicion_id_seq'::regclass);


--
-- Name: revision_inventario id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.revision_inventario ALTER COLUMN id SET DEFAULT nextval('public.revision_inventario_id_seq'::regclass);


--
-- Name: salida id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.salida ALTER COLUMN id SET DEFAULT nextval('public.salida_id_seq'::regclass);


--
-- Name: token_acceso id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.token_acceso ALTER COLUMN id SET DEFAULT nextval('public.token_acceso_id_seq'::regclass);


--
-- Name: usuario_sistema id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_sistema ALTER COLUMN id SET DEFAULT nextval('public.usuario_sistema_id_seq'::regclass);


--
-- Name: vehiculo id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehiculo ALTER COLUMN id SET DEFAULT nextval('public.vehiculo_id_seq'::regclass);


--
-- Name: ajuste_odometro ajuste_odometro_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ajuste_odometro
    ADD CONSTRAINT ajuste_odometro_pkey PRIMARY KEY (id);


--
-- Name: gasto_gasolina gasto_gasolina_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gasto_gasolina
    ADD CONSTRAINT gasto_gasolina_pkey PRIMARY KEY (id);


--
-- Name: historial_salida historial_salida_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historial_salida
    ADD CONSTRAINT historial_salida_pkey PRIMARY KEY (id);


--
-- Name: item_condicion item_condicion_nombre_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.item_condicion
    ADD CONSTRAINT item_condicion_nombre_key UNIQUE (nombre);


--
-- Name: item_condicion item_condicion_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.item_condicion
    ADD CONSTRAINT item_condicion_pkey PRIMARY KEY (id);


--
-- Name: item_inventario item_inventario_nombre_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.item_inventario
    ADD CONSTRAINT item_inventario_nombre_key UNIQUE (nombre);


--
-- Name: item_inventario item_inventario_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.item_inventario
    ADD CONSTRAINT item_inventario_pkey PRIMARY KEY (id);


--
-- Name: persona_autorizada persona_autorizada_num_licencia_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.persona_autorizada
    ADD CONSTRAINT persona_autorizada_num_licencia_key UNIQUE (num_licencia);


--
-- Name: persona_autorizada persona_autorizada_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.persona_autorizada
    ADD CONSTRAINT persona_autorizada_pkey PRIMARY KEY (id);


--
-- Name: persona_autorizada persona_autorizada_rfc_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.persona_autorizada
    ADD CONSTRAINT persona_autorizada_rfc_key UNIQUE (rfc);


--
-- Name: presupuesto_gasolina presupuesto_gasolina_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.presupuesto_gasolina
    ADD CONSTRAINT presupuesto_gasolina_pkey PRIMARY KEY (id);


--
-- Name: presupuesto_gasolina presupuesto_gasolina_vehiculo_anio_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.presupuesto_gasolina
    ADD CONSTRAINT presupuesto_gasolina_vehiculo_anio_unique UNIQUE (vehiculo_id, anio);


--
-- Name: regreso regreso_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.regreso
    ADD CONSTRAINT regreso_pkey PRIMARY KEY (id);


--
-- Name: regreso regreso_salida_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.regreso
    ADD CONSTRAINT regreso_salida_id_key UNIQUE (salida_id);


--
-- Name: resguardo resguardo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resguardo
    ADD CONSTRAINT resguardo_pkey PRIMARY KEY (id);


--
-- Name: resguardo resguardo_salida_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resguardo
    ADD CONSTRAINT resguardo_salida_id_key UNIQUE (salida_id);


--
-- Name: revision_condicion revision_condicion_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.revision_condicion
    ADD CONSTRAINT revision_condicion_pkey PRIMARY KEY (id);


--
-- Name: revision_condicion revision_condicion_salida_id_item_condicion_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.revision_condicion
    ADD CONSTRAINT revision_condicion_salida_id_item_condicion_id_key UNIQUE (salida_id, item_condicion_id);


--
-- Name: revision_inventario revision_inventario_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.revision_inventario
    ADD CONSTRAINT revision_inventario_pkey PRIMARY KEY (id);


--
-- Name: revision_inventario revision_inventario_salida_id_item_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.revision_inventario
    ADD CONSTRAINT revision_inventario_salida_id_item_id_key UNIQUE (salida_id, item_id);


--
-- Name: salida salida_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.salida
    ADD CONSTRAINT salida_pkey PRIMARY KEY (id);


--
-- Name: token_acceso token_acceso_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.token_acceso
    ADD CONSTRAINT token_acceso_pkey PRIMARY KEY (id);


--
-- Name: token_acceso token_acceso_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.token_acceso
    ADD CONSTRAINT token_acceso_token_key UNIQUE (token);


--
-- Name: usuario_sistema usuario_sistema_correo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_sistema
    ADD CONSTRAINT usuario_sistema_correo_key UNIQUE (correo);


--
-- Name: usuario_sistema usuario_sistema_num_empleado_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_sistema
    ADD CONSTRAINT usuario_sistema_num_empleado_key UNIQUE (num_empleado);


--
-- Name: usuario_sistema usuario_sistema_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_sistema
    ADD CONSTRAINT usuario_sistema_pkey PRIMARY KEY (id);


--
-- Name: vehiculo vehiculo_num_economico_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehiculo
    ADD CONSTRAINT vehiculo_num_economico_key UNIQUE (num_economico);


--
-- Name: vehiculo vehiculo_num_inventario_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehiculo
    ADD CONSTRAINT vehiculo_num_inventario_key UNIQUE (num_inventario);


--
-- Name: vehiculo vehiculo_num_serie_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehiculo
    ADD CONSTRAINT vehiculo_num_serie_key UNIQUE (num_serie);


--
-- Name: vehiculo vehiculo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehiculo
    ADD CONSTRAINT vehiculo_pkey PRIMARY KEY (id);


--
-- Name: vehiculo vehiculo_placa_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehiculo
    ADD CONSTRAINT vehiculo_placa_key UNIQUE (placa);


--
-- Name: idx_gasto_gasolina_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_gasto_gasolina_fecha ON public.gasto_gasolina USING btree (fecha_gasto);


--
-- Name: idx_gasto_gasolina_presupuesto; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_gasto_gasolina_presupuesto ON public.gasto_gasolina USING btree (presupuesto_id);


--
-- Name: idx_gasto_gasolina_vehiculo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_gasto_gasolina_vehiculo ON public.gasto_gasolina USING btree (vehiculo_id);


--
-- Name: idx_historial_salida; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_historial_salida ON public.historial_salida USING btree (salida_id, fecha DESC);


--
-- Name: idx_regreso_salida; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_regreso_salida ON public.regreso USING btree (salida_id);


--
-- Name: idx_salida_persona; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_salida_persona ON public.salida USING btree (persona_id);


--
-- Name: idx_salida_vehiculo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_salida_vehiculo ON public.salida USING btree (vehiculo_id);


--
-- Name: ux_usuario_superadmin_unico; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ux_usuario_superadmin_unico ON public.usuario_sistema USING btree (es_superadmin) WHERE (es_superadmin = true);


--
-- Name: ux_vehiculo_tarjeta_gasolina; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ux_vehiculo_tarjeta_gasolina ON public.vehiculo USING btree (num_tarjeta_gasolina) WHERE ((num_tarjeta_gasolina IS NOT NULL) AND (btrim((num_tarjeta_gasolina)::text) <> ''::text));


--
-- Name: ajuste_odometro ajuste_odometro_realizado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ajuste_odometro
    ADD CONSTRAINT ajuste_odometro_realizado_por_fkey FOREIGN KEY (realizado_por) REFERENCES public.usuario_sistema(id);


--
-- Name: ajuste_odometro ajuste_odometro_vehiculo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ajuste_odometro
    ADD CONSTRAINT ajuste_odometro_vehiculo_id_fkey FOREIGN KEY (vehiculo_id) REFERENCES public.vehiculo(id);


--
-- Name: gasto_gasolina gasto_gasolina_capturado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gasto_gasolina
    ADD CONSTRAINT gasto_gasolina_capturado_por_fkey FOREIGN KEY (capturado_por) REFERENCES public.usuario_sistema(id);


--
-- Name: gasto_gasolina gasto_gasolina_presupuesto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gasto_gasolina
    ADD CONSTRAINT gasto_gasolina_presupuesto_id_fkey FOREIGN KEY (presupuesto_id) REFERENCES public.presupuesto_gasolina(id);


--
-- Name: gasto_gasolina gasto_gasolina_salida_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gasto_gasolina
    ADD CONSTRAINT gasto_gasolina_salida_id_fkey FOREIGN KEY (salida_id) REFERENCES public.salida(id);


--
-- Name: gasto_gasolina gasto_gasolina_vehiculo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gasto_gasolina
    ADD CONSTRAINT gasto_gasolina_vehiculo_id_fkey FOREIGN KEY (vehiculo_id) REFERENCES public.vehiculo(id);


--
-- Name: historial_salida historial_salida_salida_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historial_salida
    ADD CONSTRAINT historial_salida_salida_id_fkey FOREIGN KEY (salida_id) REFERENCES public.salida(id);


--
-- Name: historial_salida historial_salida_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historial_salida
    ADD CONSTRAINT historial_salida_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario_sistema(id);


--
-- Name: presupuesto_gasolina presupuesto_gasolina_vehiculo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.presupuesto_gasolina
    ADD CONSTRAINT presupuesto_gasolina_vehiculo_id_fkey FOREIGN KEY (vehiculo_id) REFERENCES public.vehiculo(id);


--
-- Name: regreso regreso_capturado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.regreso
    ADD CONSTRAINT regreso_capturado_por_fkey FOREIGN KEY (capturado_por) REFERENCES public.usuario_sistema(id);


--
-- Name: regreso regreso_salida_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.regreso
    ADD CONSTRAINT regreso_salida_id_fkey FOREIGN KEY (salida_id) REFERENCES public.salida(id);


--
-- Name: resguardo resguardo_salida_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resguardo
    ADD CONSTRAINT resguardo_salida_id_fkey FOREIGN KEY (salida_id) REFERENCES public.salida(id);


--
-- Name: revision_condicion revision_condicion_item_condicion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.revision_condicion
    ADD CONSTRAINT revision_condicion_item_condicion_id_fkey FOREIGN KEY (item_condicion_id) REFERENCES public.item_condicion(id);


--
-- Name: revision_condicion revision_condicion_salida_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.revision_condicion
    ADD CONSTRAINT revision_condicion_salida_id_fkey FOREIGN KEY (salida_id) REFERENCES public.salida(id) ON DELETE CASCADE;


--
-- Name: revision_inventario revision_inventario_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.revision_inventario
    ADD CONSTRAINT revision_inventario_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.item_inventario(id);


--
-- Name: revision_inventario revision_inventario_salida_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.revision_inventario
    ADD CONSTRAINT revision_inventario_salida_id_fkey FOREIGN KEY (salida_id) REFERENCES public.salida(id) ON DELETE CASCADE;


--
-- Name: salida salida_capturado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.salida
    ADD CONSTRAINT salida_capturado_por_fkey FOREIGN KEY (capturado_por) REFERENCES public.usuario_sistema(id);


--
-- Name: salida salida_persona_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.salida
    ADD CONSTRAINT salida_persona_id_fkey FOREIGN KEY (persona_id) REFERENCES public.persona_autorizada(id);


--
-- Name: salida salida_vehiculo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.salida
    ADD CONSTRAINT salida_vehiculo_id_fkey FOREIGN KEY (vehiculo_id) REFERENCES public.vehiculo(id);


--
-- Name: token_acceso token_acceso_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.token_acceso
    ADD CONSTRAINT token_acceso_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario_sistema(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict u7kRNCV5PAgb1iAxfcOYiiy6TO6gcTC1tO2R6RvztOBTDQXSxGnc55T2efBGZwj

