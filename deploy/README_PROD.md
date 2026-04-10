# FinHub producción en VPS

## Estado actual
- Host: `143.47.42.218`
- Ruta: `/root/FinHub`
- Dominio: `https://finhub.vatotech.es`
- Frontend publicado por Traefik/Pangolin
- API publicada en `/api`
- Runtime actual: `SQLite` en volumen Docker `finhub_data`

## Motivo de SQLite temporal
Las migraciones Alembic del repo fallan en PostgreSQL durante la inicialización de enums, así que el despliegue operativo actual usa SQLite para dejar el servicio arriba.

## Compose actual
- fichero: `deploy/docker-compose.prod.yml`
- backend local: `127.0.0.1:8082`
- frontend local: `127.0.0.1:3010`

## Proxy
La publicación pública está definida en:
- `/opt/pangolin/config/traefik/dynamic_config.yml`

Routers:
- `finhub-frontend-router`
- `finhub-api-router`


## Backup y restore
- backup: `deploy/scripts/backup.sh`
- restore: `deploy/scripts/restore.sh /ruta/al/backup.db [ruta/al/env.backup]`

Los backups se guardan en `deploy/backups/`.
