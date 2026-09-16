# Production Deployment Guide

## Prerequisites
- Docker Engine 24+ & Docker Compose v2+
- Domain name pointed to host server
- SSL Certificate (Let's Encrypt / Certbot)

## Production Stack Launch
1. Copy `.env.prod.example` to `.env.prod` and populate production secrets.
2. Run production compose stack:
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```

## Database Backups
- Automated backup script available at `scripts/backup_db.sh`.
- Run backup:
  ```bash
  make backup
  ```
