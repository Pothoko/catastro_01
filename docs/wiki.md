# Wiki del Proyecto Catastro → Odoo

## Resumen del Proyecto

Este proyecto consiste en **migrar el sistema de catastro municipal SIICAT** (escrito en PHP + PostgreSQL) hacia una aplicación basada en **Odoo 19**, reutilizando las funcionalidades nativas de la plataforma y construyendo módulos personalizados solo donde sea necesario.

- **Sistema de origen**: SIICAT (PHP, ~298 archivos, PostgreSQL, Apache/Windows)
- **Sistema de destino**: Odoo 19.0 (Python, módulos nativos + addons custom)
- **Municipio**: Vallegrande, Bolivia
- **DB origen**: PostgreSQL en `192.168.0.150`, base de datos `vallegrande`, usuario `postgres`

---

## Módulos del Sistema Legacy (SIICAT)

### 1. Predios (Bienes Inmuebles)
- `siicat_form_predio.php` (68KB) — formulario principal de predios
- `siicat_anadir_datos.php` (89KB) — ingreso de datos prediales
- `siicat_ver_datos.php`, `siicat_ver_datos_rural.php` — visualización
- `siicat_modificar_codigo.php` (54KB) — modificación de datos
- `siicat_check_datos.php` (44KB) — validaciones
- `siicat_lista_datos.php`, `siicat_lista_datos_rural.php` — listados
- `siicat_busqueda.php`, `siicat_busqueda_resultado.php` — búsqueda avanzada
- Soporta predios **urbanos** y **rurales**

### 2. Contribuyentes / Propietarios
- `siicat_form_contrib.php` (24KB) — ficha de contribuyente
- `siicat_contrib_bienes.php` — bienes del contribuyente
- `siicat_contrib_foto.php` — fotografías
- `siicat_lista_contribuyentes.php` — listado
- `siicat_tradicion.php` (30KB) — tradición de dominio / historial

### 3. Impuestos y Colecturía
- `siicat_impuestos.php` (60KB) — gestión principal de impuestos
- `siicat_impuestos_calc.php` (90KB) — cálculo de impuestos
- `siicat_impuestos_boleta_de_pago.php` (55KB) — boletas de pago
- `siicat_impuestos_tablas.php` (99KB) — tablas de tasas e impuestos
- `siicat_impuestos_ajustes.php` (33KB) — ajustes y correcciones
- `siicat_impuestos_cotizaciones.php` (38KB) — cotizaciones
- `siicat_impuestos_transferencia.php` — impuesto por transferencia
- Reportes: ingresos recibidos, montos adeudados, boletas impresas
- Cálculo de impuestos por cuotas semestrales
- Liquidación de impuestos en transferencias de dominio

### 4. Transferencias de Dominio
- `siicat_transferencia.php` (28KB) — proceso de transferencia
- `siicat_transfer.php` (14KB) — gestión de transferencias
- `siicat_check_transferencia.php` (15KB) — validaciones
- `siicat_impuestos_generar_preliquid_transfer*.php` — preliquidaciones

### 5. Planos Catastrales (Cartografía)
- `siicat_plano_catastral_generar.php` (31KB) — generación de planos
- `siicat_generar_mapfile.php` (25KB) — generación de MapServer mapfiles
- `siicat_generar_mapfile_predio.php` — plano por predio
- `siicat_generar_mapfile_rural.php` — plano rural
- `siicat_generar_mapfile_planocatastral.php` — plano catastral completo
- `siicat_generar_dxffile.php` (11KB) — exportación DXF (AutoCAD)
- `siicat_generar_htmlfile_zoom.php` — visualización web con zoom
- Tecnología: **MapServer** + geometría PostGIS (SRID=-1, sistema local)
- Tipos: polígonos de predios, líneas divisorias, vértices, ochaves
- Certificados catastrales con plano incluido

### 6. Certificados y Documentos Oficiales
- `siicat_certificado_catastral_generar.php` (48KB) — certificado catastral
- `siicat_informe_empadronamiento_generar.php` (40KB) — informe de empadronamiento
- `siicat_informe_tecnico_generar.php` — informe técnico
- `siicat_linea_nivel_generar.php` (39KB) — línea de nivel / cota
- `siicat_linea_nivel_generar_alternativo.php` — versión alternativa
- `siicat_planos_leer_datos.php` — datos para planos
- Generados con **FPDF** (`siicat_fpdf.php`, 45KB)

### 7. Patentes Comerciales
- `siicat_form_patente.php` (19KB) — formulario de patente
- `siicat_patentes_resultado.php` (18KB) — resultados
- `siicat_patentes_rubros.php` (24KB) — rubros comerciales
- `siicat_patentes_tablas.php` (19KB) — tablas de tasas
- `siicat_patentes_licencia_generar.php` — generación de licencias
- `siicat_check_patente.php` — validaciones

### 8. Vehículos
- `siicat_form_vehic.php` (19KB) — ficha de vehículo
- `siicat_vehic_resultado.php`, `siicat_vehic_listado.php` — vistas
- `siicat_vehic_estadisticas.php` — estadísticas
- `siicat_check_vehic.php` — validaciones

### 9. Edificaciones
- `siicat_form_edif.php` (24KB) — ficha de edificación
- `siicat_ver_edif.php` (25KB) — visualización
- `siicat_check_edif.php` — validaciones
- `edificacion_valor.php` — cálculo de valores de edificación

### 10. Documentos y Adjuntos
- `docs_gestion.php`, `docs_gestion_tab.php` — gestión de documentos
- `docs_config.php` — configuración del módulo de documentos
- `docs_descargar.php` — descarga de documentos
- `siicat_upload_documento.php`, `siicat_upload_foto.php`

### 11. Sistema / Administración
- `siicat_usuarios.php` (29KB) — gestión de usuarios y roles
- `siicat_herramientas.php` (27KB) — herramientas del sistema
- `siicat_backup.php` (20KB) — backup de base de datos
- `siicat_sistema.php` (10KB) — configuración del sistema
- `siicat_cambios.php` (20KB) — auditoría de cambios
- `siicat_registro.php` (17KB) — registro de actividad

### 12. Gravámenes e Hipotecas
- `siicat_gravamen.php` (13KB) — gestión de gravámenes sobre predios

### 13. Datos Socioeconómicos
- `siicat_datos_socioeco.php` (16KB) — datos socioeconómicos del predio

---

## Arquitectura de Destino (Odoo 19)

### Módulos Nativos de Odoo a Reutilizar

| Módulo SIICAT | Módulo Odoo Nativo | Notas |
|---------------|-------------------|-------|
| Contribuyentes | `res.partner` | Ya incluye contactos, fotos, direcciones |
| Impuestos | `account` (Contabilidad) | Facturas, pagos, cuentas por cobrar |
| Boletas de pago | `account.payment`, `account.move` | Flujo de cobranza nativo |
| Documentos | `documents` | Módulo de gestión documental |
| Usuarios | `res.users`, `res.groups` | Sistema de roles y permisos |
| Auditoría | `mail.thread` (chatter) | Seguimiento de cambios en registros |
| Backup | Admin → Database Manager | Panel de Odoo |
| Vehículos | `fleet` | Módulo Fleet de Odoo |
| Patentes/Licencias | `sale` o `helpdesk` (v19) | A evaluar |

### Módulos Custom a Desarrollar (`addons/`)

| Módulo | Nombre Técnico | Prioridad |
|--------|---------------|-----------|
| Predios catastrales | `catastro_predio` | Alta |
| Planos + Cartografía | `catastro_mapa` | Media |
| Certificados PDF | `catastro_certificados` | Alta |
| Impuestos prediales | `catastro_impuestos` | Alta |
| Transferencias de dominio | `catastro_transferencia` | Alta |
| Línea de nivel / informes | `catastro_informes` | Media |
| Gravámenes | `catastro_gravamen` | Media |

---

## Infraestructura

### Entorno de Desarrollo

- **Host**: Windows 11 con WSL2 (distro: `catastro`)
- **Acceso al stack**: `wsl.exe -d catastro -u root`
- **Compose ubicado en**: `/opt/catastro/docker-compose.yml` (dentro de WSL)
- **Red proxy**: `web-proxy` (Docker network externa compartida)

### Stack Docker

```
┌─────────────────────────────────────────┐
│  Windows Host                            │
│  ┌────────────────────────────────────┐  │
│  │  WSL2: catastro                    │  │
│  │  ┌──────────────────────────────┐  │  │
│  │  │  Traefik :80/:8080           │  │  │
│  │  │  (traefik:latest)            │  │  │
│  │  ├──────────────────────────────┤  │  │
│  │  │  Odoo :8069/:8072            │  │  │
│  │  │  (odoo:19.0)                 │  │  │
│  │  ├──────────────────────────────┤  │  │
│  │  │  PostgreSQL :5432            │  │  │
│  │  │  (postgres:16)               │  │  │
│  │  └──────────────────────────────┘  │  │
│  └────────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### Versiones

| Servicio | Imagen | Versión |
|----------|--------|---------|
| Odoo | `odoo:19.0` | 19.0-20260324 |
| PostgreSQL | `postgres:16` | 16.x |
| Traefik | `traefik:latest` | v3.x |
| Docker | — | 29.3.1 |

### Routing (Traefik)

| Router | Regla | Backend |
|--------|-------|---------|
| `odoo-catastro` | `Host('catastro.local')` | Puerto 8069 |
| `odoo-catastro-ws` | `Host('catastro.local') && PathPrefix('/websocket')` | Puerto 8072 (longpolling) |

### Credenciales

| Servicio | Usuario | Contraseña |
|---------|---------|-----------|
| PostgreSQL | `odoo` | `odoo_secret` |
| Odoo master password | — | `catastro_admin_2026` |

### Archivos de Configuración

```
/home/kali/catastro/           ← repositorio git
├── README.md
├── docker-compose.yml         ← sincronizado en /opt/catastro/ (WSL)
├── config/
│   └── odoo.conf              ← configuración de Odoo
├── addons/                    ← módulos custom (vacío, pendiente desarrollo)
├── docs/
│   └── wiki.md                ← este archivo
├── siicat/                    ← código PHP legacy (referencia)
└── paria/                     ← utilidad de exportación HTML→Word
```

### Volúmenes Docker

| Volumen | Contenido |
|---------|-----------|
| `catastro_odoo-db-data` | Datos PostgreSQL |
| `catastro_odoo-web-data` | Filestore Odoo (adjuntos, imágenes) |

---

## Historial de Cambios de Infraestructura

### 2026-03-25 — Setup inicial + fixes

1. **Creado stack Docker** con `traefik:v3.3`, `odoo:19.0`, `postgres:16`
2. **Fix Docker API version**: `traefik:v3.3` incompatible con Docker 29.3.1 (API client v1.24 vs requerido v1.40+) → cambiado a `traefik:latest`
3. **Fix password mismatch**: `odoo.conf` tenía `db_password = odoo_secret` pero el compose tenía `POSTGRES_PASSWORD=odoo` → alineados a `odoo_secret`
4. **Red `web-proxy`**: red Docker externa creada previamente para compartir Traefik entre proyectos
5. **Estado final**: todos los contenedores activos, Odoo respondiendo HTTP 303 (redirecta al selector de base de datos — primer arranque)

---

## Plan de Migración (Roadmap)

### Fase 1 — Infraestructura y Setup (✅ Completado)
- [x] Stack Docker funcionando en WSL `catastro`
- [x] Odoo 19 accesible via Traefik en `catastro.local`
- [x] PostgreSQL configurado y conectado
- [x] Estructura de directorios del repositorio

### Fase 2 — Configuración Inicial Odoo
- [ ] Crear base de datos en Odoo (selector en primer arranque)
- [ ] Instalar módulos nativos: Contactos, Contabilidad, Documentos, Fleet
- [ ] Configurar Plan de Cuentas para municipio boliviano
- [ ] Configurar impuestos y tasas base
- [ ] Configurar usuarios y roles equivalentes al sistema SIICAT

### Fase 3 — Módulo Predios (`catastro_predio`)
- [ ] Análisis de la estructura de datos de `vallegrande.predios` (BD PostgreSQL origen)
- [ ] Definición del modelo `catastro.predio` (hereda `res.partner` o standalone)
- [ ] Formulario de predio con campos: clave catastral, zona, sector, colindantes
- [ ] Soporte para predios urbanos y rurales
- [ ] Historial de propietarios (tradición de dominio)

### Fase 4 — Impuestos Prediales (`catastro_impuestos`)
- [ ] Análisis de fórmulas de cálculo en `siicat_impuestos_calc.php`
- [ ] Modelo de tasas e impuestos configurables por año
- [ ] Integración con `account.move` para facturas de impuestos
- [ ] Generación de boletas de pago en PDF (FPDF → Odoo QWeb)
- [ ] Módulo de caja / colecturía

### Fase 5 — Certificados y Documentos
- [ ] Templates QWeb para certificado catastral
- [ ] Template QWeb para informe de empadronamiento
- [ ] Template QWeb para línea de nivel
- [ ] Integración con módulo Documentos de Odoo

### Fase 6 — Planos y Cartografía (`catastro_mapa`)
- [ ] Evaluar integración con OpenLayers o Leaflet en vistas Odoo
- [ ] Reemplazar MapServer por solución web (GeoServer / servidor de tiles)
- [ ] Importación de geometrías PostGIS al nuevo esquema
- [ ] Exportación DXF desde Odoo

### Fase 7 — Patentes y Vehículos
- [ ] Módulo de patentes usando `sale.order` o flujo propio
- [ ] Integración con módulo `fleet` de Odoo para vehículos
- [ ] Reportes de estadísticas

### Fase 8 — Migración de Datos
- [ ] Script de migración: `vallegrande` → PostgreSQL Odoo
- [ ] Migración de contribuyentes → `res.partner`
- [ ] Migración de predios → `catastro.predio`
- [ ] Migración de historial de impuestos → `account.move`
- [ ] Validación y reconciliación de datos

---

## Referencias

- [Código fuente legacy](../siicat/) — sistema PHP SIICAT
- [docker-compose.yml](../docker-compose.yml) — stack actual
- [config/odoo.conf](../config/odoo.conf) — configuración Odoo
- [Odoo 19 Developer Docs](https://www.odoo.com/documentation/19.0/)
- [Odoo ORM Reference](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html)
