#!/bin/bash
set -e

if [ -z "$1" ]; then
  echo "Usage: ./scripts/restore_db.sh <path_to_backup_file.sql.gz>"
  exit 1
fi

BACKUP_FILE="$1"
CONTAINER_NAME="${CONTAINER_NAME:-axontimehr-postgres}"
DB_NAME="${POSTGRES_DB:-axontimehr}"
DB_USER="${POSTGRES_USER:-axontimehr}"

echo "==> Restoring database '$DB_NAME' from '$BACKUP_FILE'..."
gunzip -c "$BACKUP_FILE" | docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME"

echo "==> Database Restoration Complete!"
