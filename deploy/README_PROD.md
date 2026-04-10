# FinHub producción en VPS

## Estado actual
- Host: `143.47.42.218`
- Ruta: `/root/FinHub`
- Dominio: `https://finhub.vatotech.es`
- Frontend publicado por Traefik/Pangolin
- API publicada en `/api`
- Runtime actual: `PostgreSQL 16`

## Compose actual
- fichero: `deploy/docker-compose.prod.yml`
- backend local: `127.0.0.1:8082`
- frontend local: `127.0.0.1:3010`
- postgres: servicio `finhub-postgres`

## Proxy
La publicación pública está definida en:
- `/opt/pangolin/config/traefik/dynamic_config.yml`

Routers:
- `finhub-frontend-router`
- `finhub-api-router`

## Backup y restore
- backup: `deploy/scripts/backup.sh`
- restore: `deploy/scripts/restore.sh /ruta/al/backup.dump [ruta/al/env.backup]`

Los backups se guardan en `deploy/backups/`.

## Flujo staging + promote

### Staging local del repo
- levantar staging: `./deploy/scripts/staging-up.sh`
- comprobar staging: `./deploy/scripts/staging-check.sh`
- parar staging: `./deploy/scripts/staging-down.sh`

Puertos usados:
- frontend staging: `http://127.0.0.1:13010`
- backend staging: `http://127.0.0.1:18082/api/health`

### Solicitud de promote

Cuando alguien termine cambios y quiera pedir despliegue:

```bash
./deploy/scripts/request-promote.sh
```

Eso genera `deploy/.last-promote-request.txt` con commit, rama y estado de staging, listo para pasárselo a Alejandro/Vato.

### Promote a producción

Solo cuando staging esté validado:

```bash
./deploy/scripts/promote-prod.sh
```

Hace backup, rebuild y levanta producción de nuevo antes de validar health.
