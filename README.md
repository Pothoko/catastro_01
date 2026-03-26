# Catastro Municipal Vallegrande — Odoo 17 LTS

Sistema de Catastro Municipal migrado de PHP/PostgreSQL (`siicat/`) a **Odoo 17 LTS** sobre Docker.

## Arquitectura

```
GitHub (repo) ──push──▶ GitHub Actions ──build──▶ GHCR (imagen Docker)
                                                          │
WSL 'catastro' (/opt/catastro) ◀──docker pull────────────┘
       │
  docker compose up -d
       │
  ┌────▼──────┐   ┌──────────┐
  │ odoo:17   │◀──│ postgres │
  └────┬──────┘   └──────────┘
       │
  Traefik → http://catastro.local
```

## Acceso rápido

| Servicio          | URL                          |
|-------------------|------------------------------|
| Odoo              | http://catastro.local/       |
| Traefik Dashboard | http://catastro.local:8080/  |

> **Prerequisito**: agregar `127.0.0.1 catastro.local` al archivo `hosts` del sistema.

---

## Deploy en producción (WSL catastro)

### Primera vez

```bash
# 1. Autenticarse en GHCR (solo una vez)
echo TU_GITHUB_PAT | docker login ghcr.io -u jpvargassoruco --password-stdin

# 2. Crear red externa de Traefik
docker network create web-proxy

# 3. Crear /opt/catastro con tu docker-compose.yml apuntando a:
#    image: ghcr.io/jpvargassoruco/catastro:latest

# 4. Levantar
cd /opt/catastro
docker compose up -d
```

### Actualización (tras cada push a main)

GitHub Actions construye la imagen automáticamente. Para actualizar la instancia:

```bash
bash /opt/catastro/scripts/deploy.sh
```

El script hace `docker pull` de la última imagen y recrea solo el contenedor Odoo (DB y Traefik no se interrumpen).

---

## Desarrollo local (Kali)

Los addons se montan como volumen para edición en caliente:

```bash
cd /home/kali/catastro
docker compose up -d          # usa ghcr.io/jpvargassoruco/catastro:latest
docker logs catastro-odoo-1 -f
```

Para probar cambios en addons sin rebuild de imagen, Odoo los detecta con el volumen montado. Para producción, hacer push → Actions construye → deploy.sh actualiza.

---

## Comandos útiles

```bash
# Logs en tiempo real
docker logs catastro-odoo-1 -f

# Shell dentro del contenedor
docker exec -it catastro-odoo-1 bash

# Reiniciar solo Odoo (sin tocar DB)
docker compose restart odoo

# Update de módulo
docker exec catastro-odoo-1 odoo -u catastro_predio --stop-after-init

# Detener y limpiar volúmenes (¡BORRA DATOS!)
docker compose down -v
```

---

## Estructura del repositorio

```
catastro/
├── .github/workflows/
│   └── build-push.yml       # CI: build → push a GHCR en cada push a main
├── addons/
│   └── catastro_predio/     # Módulo principal (Fase 3)
├── config/
│   └── odoo.conf
├── scripts/
│   ├── deploy.sh            # Actualización zero-downtime en WSL
│   └── docker-compose.prod.yml  # Referencia compose producción
├── Dockerfile               # Odoo 17 LTS (GDAL pendiente Fase 6)
├── docker-compose.yml       # Desarrollo local
└── requirements.txt         # Dependencias Python extra
```

## Fases del proyecto

| Fase | Descripción | Estado |
|------|-------------|--------|
| 1 | Análisis legacy SIICAT | ✅ |
| 2 | Infraestructura Docker + CI/CD | ✅ |
| 3 | Módulo `catastro_predio` | ✅ |
| 4 | Valuación y avalúos | 🔜 |
| 5 | Reportes y certificados | 🔜 |
| 6 | GIS / Base Geoengine | 🔜 |
| 7 | Migración de datos SIICAT | 🔜 |

## Documentación técnica

Ver [`docs/wiki.md`](docs/wiki.md) para arquitectura detallada, decisiones de diseño y mapeo SIICAT → Odoo.
