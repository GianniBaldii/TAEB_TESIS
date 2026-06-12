#!/usr/bin/env sh
set -eu

DUMP_DIR="docker/mysql/dumps"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
DUMP_FILE="${1:-taeb_${TIMESTAMP}.sql}"

mkdir -p "$DUMP_DIR"

docker compose exec -T db sh -c \
    'export MYSQL_PWD="$MYSQL_PASSWORD"; \
    exec mysqldump --single-transaction --routines --triggers --no-tablespaces \
    -u"$MYSQL_USER" "$MYSQL_DATABASE"' \
    > "$DUMP_DIR/$DUMP_FILE"

printf 'Dump creado en %s\n' "$DUMP_DIR/$DUMP_FILE"
