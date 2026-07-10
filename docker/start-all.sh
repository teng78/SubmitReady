#!/bin/sh
set -eu

uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log &
api_pid=$!
trap 'kill "$api_pid" 2>/dev/null || true' EXIT INT TERM
nginx -c /etc/nginx/nginx.conf -g 'daemon off;'
