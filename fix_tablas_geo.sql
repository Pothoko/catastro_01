-- ============================================================
-- Script de rescate: Crear tablas con geometría manualmente
-- (Evita las comas trailing y restricciones de SRID del backup)
-- ============================================================

-- Tabla PREDIOS (la más importante)
CREATE TABLE IF NOT EXISTS predios (
    id_predio integer NOT NULL,
    cod_geo character varying(11) NOT NULL,
    cod_uv smallint,
    cod_man smallint,
    cod_pred smallint,
    activo smallint,
    the_geom geometry,
    nompro character varying(50),
    nomvia character varying(254),
    ser_alc character varying(2),
    ser_agu character varying(2),
    ser_luz character varying(2),
    superficie numeric(10,3),
    verificado character(10),
    "fecha de verificacion" date,
    inf_pre boolean,
    via_mat character(3),
    fotos character(2),
    edi_suptot numeric(10,3),
    tip_inm character(3),
    ser_tel character(2),
    via_tipo character(3),
    ter_top character(3),
    val_zon smallint,
    edi_sup numeric(10,3) DEFAULT 0,
    dir_bar character(254),
    ter_uso character(3),
    imp_pag smallint,
    dir_urb character(254)
);

CREATE SEQUENCE IF NOT EXISTS predios_id_predio_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER SEQUENCE predios_id_predio_seq OWNED BY predios.id_predio;
ALTER TABLE ONLY predios ALTER COLUMN id_predio SET DEFAULT nextval('predios_id_predio_seq'::regclass);

-- Tabla PREDIOS_OCHA
CREATE TABLE IF NOT EXISTS predios_ocha (
    id_predio integer NOT NULL,
    cod_geo character varying NOT NULL,
    cod_uv smallint,
    cod_man smallint,
    cod_pred smallint,
    activo smallint,
    the_geom geometry,
    area numeric(10,3)
);

CREATE SEQUENCE IF NOT EXISTS predios_ocha_id_predio_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER SEQUENCE predios_ocha_id_predio_seq OWNED BY predios_ocha.id_predio;
ALTER TABLE ONLY predios_ocha ALTER COLUMN id_predio SET DEFAULT nextval('predios_ocha_id_predio_seq'::regclass);

-- Tabla PREDIOS_OCHA_ORIG
CREATE TABLE IF NOT EXISTS predios_ocha_orig (
    cod_geo character varying NOT NULL,
    cod_uv smallint,
    cod_man smallint,
    cod_pred smallint,
    the_geom geometry
);

-- Tabla MANZANOS
CREATE TABLE IF NOT EXISTS manzanos (
    cod_geo character varying(11) NOT NULL,
    cod_uv smallint NOT NULL,
    cod_man smallint NOT NULL,
    the_geom geometry
);

-- Tabla MANCHAURBANA
CREATE TABLE IF NOT EXISTS manchaurbana (
    cod_geo character varying(11) NOT NULL,
    cod_uv smallint NOT NULL,
    the_geom geometry
);

-- Tabla MATERIAL_DE_VIA
CREATE TABLE IF NOT EXISTS material_de_via (
    material character(3),
    the_geom geometry
);

-- Tabla OBJETOS
CREATE TABLE IF NOT EXISTS objetos (
    id integer,
    descrip character varying(30),
    observ character varying(30),
    the_geom geometry
);

-- Tabla OBJETOS_LINEA
CREATE TABLE IF NOT EXISTS objetos_linea (
    id smallint,
    cod_geo character varying NOT NULL,
    descrip character varying,
    observ character varying,
    the_geom geometry
);

-- Tabla OCHAVES_LINEA
CREATE TABLE IF NOT EXISTS ochaves_linea (
    id integer,
    cod_geo character varying NOT NULL,
    cod_uv smallint,
    cod_man smallint,
    cod_pred smallint,
    pos character varying,
    radio character varying,
    the_geom geometry
);

-- Tabla PRUEBA
CREATE TABLE IF NOT EXISTS prueba (
    gid integer NOT NULL,
    id integer,
    the_geom geometry
);

CREATE SEQUENCE IF NOT EXISTS prueba_gid_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER SEQUENCE prueba_gid_seq OWNED BY prueba.gid;
ALTER TABLE ONLY prueba ALTER COLUMN gid SET DEFAULT nextval('prueba_gid_seq'::regclass);

-- Tabla TEMP_LINE
CREATE TABLE IF NOT EXISTS temp_line (
    user_id character varying,
    id integer DEFAULT 99,
    cod_cat character varying(11),
    nombre character varying,
    descrip character varying,
    tipo character varying,
    the_geom geometry
);

-- Tabla TEMP_POINT
CREATE TABLE IF NOT EXISTS temp_point (
    id integer,
    user_id character varying,
    cod_cat character varying,
    text character varying,
    pos character varying DEFAULT '99',
    descrip character varying,
    the_geom geometry
);

-- Tabla TEMP_POLY
CREATE TABLE IF NOT EXISTS temp_poly (
    user_id character varying,
    cod_cat character varying,
    cod_uv smallint,
    cod_man smallint,
    cod_pred smallint,
    cod_blq smallint,
    cod_piso smallint,
    cod_apto smallint,
    edi_num smallint,
    edi_piso smallint,
    numero smallint,
    label character varying,
    the_geom geometry,
    cod_geo character varying
);

-- Tabla TRAMITE_DIV
CREATE TABLE IF NOT EXISTS tramite_div (
    divcod integer NOT NULL,
    precod character varying,
    divfec1 date,
    divfec2 date,
    concod1 integer,
    concod2 integer,
    concod3 integer,
    concod4 integer,
    connom1 character varying,
    connom2 character varying,
    connom3 character varying,
    connom4 character varying,
    cod_uv smallint,
    cod_man smallint,
    cod_pred smallint,
    divsol character varying,
    divtecasi character varying,
    divtecfec date,
    divtechor character varying,
    divapr character varying,
    divrestra character varying,
    divpre character varying,
    the_geom geometry,
    supsegdoc double precision,
    supsegmen double precision
);

-- Tabla URBANIZACION
CREATE TABLE IF NOT EXISTS urbanizacion (
    id_urb integer,
    cod_geo character varying(11),
    cod_uv smallint,
    nombre character varying(100),
    the_geom geometry
);

-- Tabla USO_DE_SUELO
CREATE TABLE IF NOT EXISTS uso_de_suelo (
    uso character varying,
    the_geom geometry
);

-- Tabla ZONAS
CREATE TABLE IF NOT EXISTS zonas (
    zona character varying,
    the_geom geometry,
    cod_geo character varying(11),
    id_zona integer
);

-- Tabla AREAURBANA
CREATE TABLE IF NOT EXISTS areaurbana (
    cod_geo character varying(11),
    geom geometry
);

-- Tabla BARRIOS
CREATE TABLE IF NOT EXISTS barrios (
    nombre character varying,
    cod_geo character varying(11),
    id_barrio integer,
    the_geom geometry
);

-- Tabla CALLES
CREATE TABLE IF NOT EXISTS calles (
    id integer,
    cod_geo character varying(11),
    tipo character varying,
    descrip character varying,
    nombre character varying,
    observ character varying,
    the_geom geometry,
    via_mat character varying,
    ser_agu character varying,
    ser_ene character varying,
    ser_alc character varying,
    ser_tel character varying,
    ser_gas character varying
);

-- Tabla CENTROPOBLADOS
CREATE TABLE IF NOT EXISTS centropoblados (
    th_geom geometry,
    cod_geo character varying(11),
    cod_uv smallint,
    nombre character varying,
    cod_dis smallint,
    ley_creacion1 character varying,
    ley_creacion2 character varying
);

-- Tabla DISTRITOS
CREATE TABLE IF NOT EXISTS distritos (
    cod_geo character varying(11),
    cod_uv smallint,
    the_geom geometry,
    nombre character varying,
    area double precision,
    cod_dis smallint
);

-- Tabla EDIFICACION_BAS
CREATE TABLE IF NOT EXISTS edificacion_bas (
    id integer NOT NULL,
    geom geometry,
    gid integer,
    cod_piso smallint,
    cod_geo character varying(11),
    cod_uv smallint,
    cod_man smallint,
    cod_pred smallint,
    edi_piso smallint,
    cod_blo smallint,
    edi_num smallint
);

-- Tabla EDIFICACIONES
CREATE TABLE IF NOT EXISTS edificaciones (
    id_edif integer NOT NULL,
    cod_geo character varying(11),
    cod_uv smallint,
    cod_man smallint,
    cod_pred smallint,
    edi_num smallint,
    edi_piso smallint,
    the_geom geometry,
    edi_esp character varying,
    cod_blo smallint,
    edi_are numeric(10,2)
);

-- Tabla GRILLA
CREATE TABLE IF NOT EXISTS grilla (
    id integer,
    x1 double precision,
    y1 double precision,
    x2 double precision,
    y2 double precision,
    the_geom geometry
);

-- Tabla UV
CREATE TABLE IF NOT EXISTS uv (
    gid integer NOT NULL,
    cod_uv character varying,
    the_geom geometry
);

SELECT 'Tablas con geometría creadas exitosamente' AS resultado;
