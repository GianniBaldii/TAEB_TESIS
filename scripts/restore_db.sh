#!/usr/bin/env sh
set -eu

if [ "$#" -ne 1 ]; then
    printf 'Uso: %s <archivo.sql>\n' "$0" >&2
    exit 1
fi

case "$1" in
    /*) DUMP_FILE="$1" ;;
    *) DUMP_FILE="docker/mysql/dumps/$1" ;;
esac

if [ ! -f "$DUMP_FILE" ]; then
    printf 'No se encontró el archivo: %s\n' "$DUMP_FILE" >&2
    exit 1
fi

docker compose exec -T db sh -c \
    'export MYSQL_PWD="$MYSQL_PASSWORD"; \
    exec mysql -u"$MYSQL_USER" "$MYSQL_DATABASE"' \
    < "$DUMP_FILE"

printf 'Base restaurada desde %s\n' "$DUMP_FILE"
