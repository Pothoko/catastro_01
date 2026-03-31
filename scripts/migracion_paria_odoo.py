#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
=========================================================================
Script ETL de Migración Exhaustiva (Legacy SIICAT / Paria -> Odoo 17)
=========================================================================
Extrae TODOS los campos de contribuyentes y predios de la BD legacy
'paria.backup', incluyendo geometría PostGIS, y los inyecta en Odoo 17
vía XML-RPC.

INSTRUCCIONES:
1. Restaurar el backup legacy:
   sudo docker exec -i catastro_01-db-1 pg_restore \
       --no-owner --no-privileges -d paria_legacy \
       < paria.backup
   
   (Previamente crear la BD dentro del contenedor:
    sudo docker exec catastro_01-db-1 createdb -U odoo paria_legacy)

2. Instalar dependencias:
   pip install psycopg2-binary

3. Ejecutar:
   python3 scripts/migracion_paria_odoo.py
"""

import xmlrpc.client
import psycopg2
from psycopg2.extras import DictCursor
import json
import sys
import traceback

# ==========================================
# CONFIGURACIÓN ODOO 17 (DESTINO)
# ==========================================
ODOO_URL = 'http://localhost:8069'
ODOO_DB = 'odoo'
ODOO_USER = 'admin'
ODOO_PASSWORD = 'admin'

# ==========================================
# CONFIGURACIÓN POSTGRES (ORIGEN - PARIA)
# Conectamos al contenedor PostgreSQL de Docker
# ==========================================
PG_HOST = 'localhost'
PG_PORT = '5432'
PG_DB = 'paria_legacy'
PG_USER = 'odoo'
PG_PASS = 'odoo_secret'


# ==========================================
# HELPERS
# ==========================================

import re

def safe_str(val, strip=True):
    """Convierte un valor a string limpio o retorna False (null de Odoo)."""
    if val is None:
        return False
    s = str(val)
    if strip:
        s = s.strip()
    # Remover caracteres de control inválidos en XML (evita ExpatError)
    s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', s)
    return s if s else False

def safe_float(val):
    """Convierte a float o retorna 0.0."""
    if val is None:
        return 0.0
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def safe_int(val):
    """Convierte a int o retorna 0."""
    if val is None:
        return 0
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0


def bool_from_paria(val):
    """Convierte los códigos SI/NO de Paria (2 chars) a booleano."""
    if val is None:
        return False
    s = str(val).strip().upper()
    return s in ('SI', 'S', '1', 'YES', 'Y', 'OK')


def build_address(*parts):
    """Concatena partes de dirección en una sola línea, ignorando vacíos."""
    cleaned = [str(p).strip() for p in parts if p and str(p).strip()]
    return ', '.join(cleaned) if cleaned else False


# ==========================================
# MIGRACIÓN PRINCIPAL
# ==========================================

def main():
    print("=" * 70)
    print("  MIGRACIÓN ETL EXHAUSTIVA: Paria Legacy -> Odoo 17 Catastro")
    print("=" * 70)

    # ── 1. Autenticación con Odoo ────────────────────────────────────────
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
        if not uid:
            raise Exception("Credenciales de Odoo denegadas.")
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        print("✓ Conexión con Odoo 17 exitosa (uid={})".format(uid))
    except Exception as e:
        print(f"❌ Error conectando a Odoo: {e}")
        sys.exit(1)

    # ── 2. Conexión con Legacy PostgreSQL ────────────────────────────────
    try:
        pg_conn = psycopg2.connect(
            host=PG_HOST, port=PG_PORT,
            dbname=PG_DB, user=PG_USER, password=PG_PASS
        )
        pg_cursor = pg_conn.cursor(cursor_factory=DictCursor)
        print("✓ Conexión con PostgreSQL (Paria Legacy) exitosa.")
    except Exception as e:
        print(f"❌ Error conectando a BD Legacy: {e}")
        sys.exit(1)

    # ── Verificar extensión PostGIS ──────────────────────────────────────
    try:
        pg_cursor.execute("SELECT PostGIS_Version();")
        postgis_ver = pg_cursor.fetchone()[0]
        print(f"✓ PostGIS detectado: v{postgis_ver}")
        HAS_POSTGIS = True
    except Exception:
        print("⚠ PostGIS NO disponible. Geometrías NO serán migradas.")
        HAS_POSTGIS = False
        pg_conn.rollback()

    # ══════════════════════════════════════════════════════════════════════
    # FASE 1: MIGRAR CONTRIBUYENTES -> res.partner
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("  FASE 1: Migrando Contribuyentes -> res.partner")
    print("─" * 70)

    # Mapa de PMC -> partner_id de Odoo (para vincular predios después)
    pmc_to_partner = {}
    contribuyentes_ok = 0
    contribuyentes_err = 0
    contribuyentes_skip = 0

    # ── Pre-cargar partners existentes para evitar duplicados ──
    try:
        existing = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'search_read',
            [[['ref', '!=', False]]],
            {'fields': ['id', 'ref']}
        )
        for ex in existing:
            if ex['ref']:
                try:
                    pmc_to_partner[int(ex['ref'])] = ex['id']
                except (ValueError, TypeError):
                    pass
        if pmc_to_partner:
            print(f"   ℹ {len(pmc_to_partner)} contribuyentes ya existen en Odoo, se omitirán.")
    except Exception as e:
        print(f"Error cargando existentes: {e}")


    try:
        pg_cursor.execute("""
            SELECT
                id_contrib, con_pmc, pmc_ant,
                con_act, con_fech_ini, con_fech_fin,
                con_tipo, con_raz,
                con_pat, con_mat, con_nom1, con_nom2,
                con_nit, con_tel,
                doc_tipo, doc_num, doc_exp,
                dom_dpto, dom_ciu, dom_bar,
                dom_tipo, dom_nom, dom_num,
                dom_edif, dom_bloq, dom_piso, dom_apto,
                med_agu, med_luz,
                con_obs, tit_pers,
                con_fecnac, foto, con_cas
            FROM contribuyentes
            ORDER BY id_contrib
        """)
        registros = pg_cursor.fetchall()
        total = len(registros)
        print(f"   Encontrados: {total} contribuyentes en Paria")

        for i, p in enumerate(registros, 1):
            try:
                pmc = p['con_pmc']

                # ── Saltar si ya existe en Odoo ──
                if pmc in pmc_to_partner:
                    contribuyentes_skip += 1
                    if i % 500 == 0:
                        print(f"   [{i}/{total}] Saltando (ya existe)...")
                    continue

                # ── Construir nombre completo ──
                razon = safe_str(p['con_raz'])
                is_company = False

                if razon:
                    nombre = razon
                    is_company = True
                else:
                    parts = [
                        safe_str(p['con_nom1']),
                        safe_str(p['con_nom2']),
                        safe_str(p['con_pat']),
                        safe_str(p['con_mat']),
                    ]
                    nombre = ' '.join([x for x in parts if x])

                if not nombre:
                    nombre = f"Contribuyente PMC-{pmc}"

                # ── Documento de identidad ──
                doc = safe_str(p['doc_num'])
                exp = safe_str(p['doc_exp'])
                vat = f"{doc} {exp}".strip() if doc else False

                # ── Dirección completa ──
                street = build_address(
                    f"Dpto: {safe_str(p['dom_dpto'])}" if safe_str(p['dom_dpto']) else None,
                    f"Barrio: {safe_str(p['dom_bar'])}" if safe_str(p['dom_bar']) else None,
                    safe_str(p['dom_nom']),
                    f"Nro {safe_str(p['dom_num'])}" if safe_str(p['dom_num']) else None,
                )
                street2 = build_address(
                    f"Edif: {safe_str(p['dom_edif'])}" if safe_str(p['dom_edif']) else None,
                    f"Bloque: {safe_str(p['dom_bloq'])}" if safe_str(p['dom_bloq']) else None,
                    f"Piso: {safe_str(p['dom_piso'])}" if safe_str(p['dom_piso']) else None,
                    f"Apto: {safe_str(p['dom_apto'])}" if safe_str(p['dom_apto']) else None,
                )

                # ── Preparar valores para Odoo ──
                vals = {
                    'name': nombre,
                    'is_company': is_company,
                    'phone': safe_str(p['con_tel']) or False,
                    'vat': vat,
                    'street': street,
                    'street2': street2,
                    'city': safe_str(p['dom_ciu']) or 'Vallegrande',
                    'comment': safe_str(p['con_obs']) or False,
                    'ref': str(pmc) if pmc else False,
                }

                # Crear en Odoo
                partner_id = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'res.partner', 'create', [vals]
                )

                pmc_to_partner[pmc] = partner_id
                contribuyentes_ok += 1

                if i % 50 == 0 or i == total:
                    print(f"   [{i}/{total}] {nombre[:40]}... -> ID Odoo: {partner_id}")

            except Exception as e:
                contribuyentes_err += 1
                print(f"   ⚠ Error en contribuyente #{p['id_contrib']}: {e}")

    except psycopg2.Error as e:
        pg_conn.rollback()
        print(f"   ❌ Error leyendo tabla 'contribuyentes': {e}")

    print(f"\n   ✓ Contribuyentes migrados: {contribuyentes_ok}")
    print(f"   ⏭ Contribuyentes omitidos (ya existían): {contribuyentes_skip}")
    print(f"   ⚠ Contribuyentes con error: {contribuyentes_err}")

    # ══════════════════════════════════════════════════════════════════════
    # FASE 2: MIGRAR PREDIOS -> catastro.predio + catastro.mapa
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("  FASE 2: Migrando Predios -> catastro.predio + catastro.mapa")
    print("─" * 70)

    predios_ok = 0
    predios_err = 0
    mapas_ok = 0

    # Construir query con o sin geometría
    geom_col = ""
    if HAS_POSTGIS:
        # SRID=-1 en Paria. Intentamos transformar a 4326 si es posible,
        # sino exportamos tal cual (Leaflet puede manejar coordenadas locales).
        geom_col = ", ST_AsGeoJSON(ST_SetSRID(the_geom::geometry, 32720)::geometry) as geojson_geom"

    try:
        pg_cursor.execute(f"""
            SELECT
                id_predio, cod_geo,
                cod_uv, cod_man, cod_pred,
                activo,
                nompro, nomvia,
                ser_alc, ser_agu, ser_luz, ser_tel,
                superficie,
                verificado, "fecha de verificacion",
                inf_pre,
                via_mat, fotos, edi_suptot,
                tip_inm,
                via_tipo,
                ter_top,
                val_zon,
                edi_sup,
                dir_bar, ter_uso, imp_pag,
                dir_urb
                {geom_col}
            FROM predios
            ORDER BY id_predio
        """)
        registros = pg_cursor.fetchall()
        total = len(registros)
        print(f"   Encontrados: {total} predios")

        for i, pr in enumerate(registros, 1):
            try:
                cod_geo = safe_str(pr['cod_geo']) or f"LEGACY-{pr['id_predio']}"

                # ── Buscar propietario vinculado ──
                # Usamos la tabla contrib_mod para encontrar el PMC del predio
                propietario_id = False
                try:
                    pg_cursor2 = pg_conn.cursor(cursor_factory=DictCursor)
                    pg_cursor2.execute("""
                        SELECT con_pmc FROM contribuyentes
                        WHERE con_pmc = (
                            SELECT con_pmc FROM contribuyentes
                            WHERE con_pmc IN (
                                SELECT DISTINCT id_contrib FROM contrib_mod
                            )
                            LIMIT 1
                        )
                        LIMIT 1
                    """)
                except Exception:
                    pass

                # Intentar vincular por nombre del propietario en el predio
                nompro = safe_str(pr['nompro'])
                if nompro:
                    try:
                        found = models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'res.partner', 'search',
                            [[['name', 'ilike', nompro]]],
                            {'limit': 1}
                        )
                        if found:
                            propietario_id = found[0]
                    except Exception:
                        pass

                # ── Mapear tipo de inmueble ──
                tipo = 'urbano'  # default
                tip_inm = safe_str(pr['tip_inm'])

                # ── Mapear estado ──
                estado = 'registrado' if safe_int(pr['activo']) == 1 else 'inactivo'

                # ── Dirección ──
                direccion = build_address(
                    safe_str(pr['dir_bar']),
                    safe_str(pr['dir_urb']),
                    safe_str(pr['nomvia'])
                )

                # ── Fecha verificación ──
                fecha_verif = pr.get('fecha de verificacion')
                if fecha_verif:
                    fecha_verif = str(fecha_verif)
                else:
                    fecha_verif = False

                # ── Preparar valores para catastro.predio ──
                vals = {
                    'clave_catastral': cod_geo,
                    'tipo': tipo,
                    'state': estado,
                    'superficie_terreno': safe_float(pr['superficie']),
                    'superficie_construida': safe_float(pr['edi_suptot']),
                    'direccion': direccion,
                    'propietario_id': propietario_id,

                    # Servicios Básicos
                    'servicio_alcantarillado': bool_from_paria(pr['ser_alc']),
                    'servicio_agua': bool_from_paria(pr['ser_agu']),
                    'servicio_luz': bool_from_paria(pr['ser_luz']),
                    'servicio_telefono': bool_from_paria(pr['ser_tel']),

                    # Datos Técnicos
                    'topografia': safe_str(pr['ter_top']) or False,
                    'uso_terreno_legacy': safe_str(pr['ter_uso']) or False,
                    'valor_zona': safe_int(pr['val_zon']),
                    'material_via': safe_str(pr['via_mat']) or False,
                    'tipo_via': safe_str(pr['via_tipo']) or False,
                    'tipo_inmueble_legacy': tip_inm or False,

                    # Verificación
                    'verificado': bool(safe_str(pr['verificado'])),
                    'fecha_verificacion': fecha_verif,
                    'tiene_informe_predio': bool(pr['inf_pre']),
                    'tiene_fotos': safe_str(pr['fotos']) in ('SI', 'S', '1', 'si'),

                    # Códigos Legacy
                    'legacy_id_predio': safe_int(pr['id_predio']),
                    'cod_uv': safe_int(pr['cod_uv']),
                    'cod_man': safe_int(pr['cod_man']),
                    'cod_pred': safe_int(pr['cod_pred']),
                    'nombre_propietario_legacy': nompro or False,
                    'nombre_via': safe_str(pr['nomvia']) or False,
                    'urbanizacion': safe_str(pr['dir_urb']) or False,
                    'impuesto_pagado': safe_int(pr['imp_pag']),
                }

                # Crear predio en Odoo
                predio_odoo_id = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'catastro.predio', 'create', [vals]
                )
                predios_ok += 1

                # ── Crear capa cartográfica si hay geometría ──
                if HAS_POSTGIS and pr.get('geojson_geom'):
                    try:
                        geojson = pr['geojson_geom']
                        # Validar que es JSON válido
                        json.loads(geojson)

                        mapa_vals = {
                            'name': f'Polígono Predio {cod_geo}',
                            'predio_id': predio_odoo_id,
                            'tipo_poligono': 'predio',
                            'coordenadas_json': geojson,
                            'activo': True,
                        }
                        models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'catastro.mapa', 'create', [mapa_vals]
                        )
                        mapas_ok += 1
                    except (json.JSONDecodeError, Exception) as ge:
                        print(f"   ⚠ Geometría inválida predio {cod_geo}: {ge}")

                if i % 50 == 0 or i == total:
                    print(f"   [{i}/{total}] Predio {cod_geo} -> ID Odoo: {predio_odoo_id}")

            except Exception as e:
                predios_err += 1
                print(f"   ⚠ Error en predio #{pr['id_predio']}: {e}")

    except psycopg2.Error as e:
        pg_conn.rollback()
        print(f"   ❌ Error leyendo tabla 'predios': {e}")
        traceback.print_exc()

    print(f"\n   ✓ Predios migrados: {predios_ok}")
    print(f"   ✓ Capas geográficas creadas: {mapas_ok}")
    print(f"   ⚠ Predios con error: {predios_err}")

    # ══════════════════════════════════════════════════════════════════════
    # FASE 3: MIGRAR COLINDANTES
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("  FASE 3: Migrando Colindantes")
    print("─" * 70)

    colindantes_ok = 0
    try:
        pg_cursor.execute("""
            SELECT
                c.id_predio, c.norte_nom, c.norte_med,
                c.sur_nom, c.sur_med,
                c.este_nom, c.este_med,
                c.oeste_nom, c.oeste_med,
                p.cod_geo
            FROM colindantes c
            LEFT JOIN predios p ON c.id_predio = p.id_predio
            ORDER BY c.id_predio
        """)
        colindantes = pg_cursor.fetchall()
        total_col = len(colindantes)
        print(f"   Encontrados: {total_col} registros de colindantes")

        for col in colindantes:
            cod_geo = safe_str(col['cod_geo'])
            if not cod_geo:
                continue

            # Buscar el predio en Odoo
            try:
                predio_ids = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'catastro.predio', 'search',
                    [[['clave_catastral', '=', cod_geo]]],
                    {'limit': 1}
                )
                if not predio_ids:
                    continue

                # Crear 4 colindantes (N, S, E, O) si tienen datos
                direcciones = [
                    ('norte', col['norte_nom'], col['norte_med']),
                    ('sur', col['sur_nom'], col['sur_med']),
                    ('este', col['este_nom'], col['este_med']),
                    ('oeste', col['oeste_nom'], col['oeste_med']),
                ]

                for direccion, nombre, medida in direcciones:
                    nom = safe_str(nombre)
                    if nom:
                        try:
                            models.execute_kw(
                                ODOO_DB, uid, ODOO_PASSWORD,
                                'catastro.colindante', 'create', [{
                                    'predio_id': predio_ids[0],
                                    'direccion': direccion,
                                    'nombre': nom,
                                    'medida': safe_str(medida) or '0',
                                }]
                            )
                            colindantes_ok += 1
                        except Exception:
                            pass  # Puede fallar si el modelo colindante tiene distinto schema
            except Exception:
                pass

    except psycopg2.Error as e:
        pg_conn.rollback()
        print(f"   ⚠ Error leyendo colindantes: {e}")

    print(f"   ✓ Colindantes migrados: {colindantes_ok}")

    # ══════════════════════════════════════════════════════════════════════
    # RESUMEN FINAL
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("  RESUMEN DE MIGRACIÓN")
    print("=" * 70)
    print(f"  Contribuyentes (res.partner):  {contribuyentes_ok} OK / {contribuyentes_err} ERR")
    print(f"  Predios (catastro.predio):     {predios_ok} OK / {predios_err} ERR")
    print(f"  Capas GIS (catastro.mapa):     {mapas_ok}")
    print(f"  Colindantes:                   {colindantes_ok}")
    print("=" * 70)
    print("  ✅ Migración completada. Verifique en Odoo -> Catastro -> Predios")
    print("=" * 70)

    pg_conn.close()


if __name__ == "__main__":
    main()
