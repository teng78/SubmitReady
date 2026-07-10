FROM node:20-alpine AS frontend-build
WORKDIR /src
COPY frontend/package*.json ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    SUBMITREADY_DATA_DIR=/data SUBMITREADY_BUILTIN_RULES_DIR=/app/examples/rules \
    SUBMITREADY_DATABASE_URL=sqlite:////data/submitready.db
RUN apt-get update \
    && apt-get install --no-install-recommends -y nginx gcc g++ make cmake ninja-build \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 submitready \
    && useradd --uid 10001 --gid submitready --create-home submitready
WORKDIR /app
COPY backend/pyproject.toml ./backend/pyproject.toml
COPY backend/app ./backend/app
RUN python -m pip install "./backend[dev]"
COPY examples/rules ./examples/rules
COPY --from=frontend-build /src/dist /usr/share/nginx/html
COPY docker/nginx-standalone.conf /etc/nginx/nginx.conf
COPY docker/start-all.sh /usr/local/bin/start-submitready
RUN chmod 755 /usr/local/bin/start-submitready \
    && mkdir -p /data/workspaces /data/rules /tmp/client_temp /tmp/proxy_temp \
    && chown -R submitready:submitready /data /app /usr/share/nginx/html /tmp/client_temp /tmp/proxy_temp
USER 10001:10001
WORKDIR /app/backend
EXPOSE 8080
CMD ["start-submitready"]
