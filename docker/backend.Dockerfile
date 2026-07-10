FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install --no-install-recommends -y gcc g++ make cmake ninja-build \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 submitready \
    && useradd --uid 10001 --gid submitready --create-home submitready

WORKDIR /app
COPY backend/pyproject.toml ./backend/pyproject.toml
COPY backend/app ./backend/app
RUN python -m pip install "./backend[dev]"
COPY examples/rules ./examples/rules
RUN mkdir -p /data/workspaces /data/rules && chown -R submitready:submitready /data /app

USER 10001:10001
WORKDIR /app/backend
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
