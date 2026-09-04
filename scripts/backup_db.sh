#!/bin/bash
set -e

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
CONTAINER_NAME="${CONTAINER_NAME:-axontimehr-postgres}"
DB_NAME="${POSTGRES_DB:-axontimehr}"
DB_USER="${POSTGRES_USER:-axontimehr}"

mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/axontimehr_backup_$TIMESTAMP.sql.gz"

echo "==> Backing up database '$DB_NAME' from container '$CONTAINER_NAME'..."
docker exec -t "$CONTAINER_NAME" pg_dump -U "$DB_USER" -d "$DB_NAME" | gzip > "$BACKUP_FILE"

echo "==> Backup complete: $BACKUP_FILE"
