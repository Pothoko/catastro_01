# Catastro → Odoo Migration Project

Sistema de Catastro Municipal migrado de PHP/PostgreSQL a **Odoo 19** sobre Docker.

## Objetivo

Reemplazar la aplicación PHP legacy (`siicat/`) por módulos de Odoo 19 que reutilicen las funcionalidades nativas de la plataforma (Partners, Accounting, Fleet, etc.) y agreguen módulos customizados donde sea necesario.

## Documentación

Toda la documentación técnica y de planificación se encuentra en [`docs/wiki.md`](docs/wiki.md).

## Acceso rápido

| Servicio | URL |
|----------|-----|
| Odoo | http://catastro.local/ |
| Traefik Dashboard | http://catastro.local:8080/ |

> **Prerequisito**: agregar `127.0.0.1 catastro.local` al archivo hosts del sistema.

## Comandos útiles

```bash
# Dentro de WSL 'catastro'
cd /opt/catastro

# Levantar stack
docker compose up -d

# Ver logs de Odoo
docker logs catastro-odoo-1 -f

# Detener y limpiar volúmenes (¡borra datos!)
docker compose down -v
```
