FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SUBMITREADY_DATA_DIR=/data \
    SUBMITREADY_DATABASE_URL=sqlite:////data/submitready.db \
    SUBMITREADY_BUILTIN_RULES_DIR=/rules \
    SUBMITREADY_ALLOW_UNTRUSTED_EXECUTION=false

RUN addgroup --system submitready && adduser --system --ingroup submitready submitready
WORKDIR /app
COPY backend/pyproject.toml ./pyproject.toml
COPY backend/app ./app
COPY examples/rules /rules
RUN pip install --no-cache-dir . && mkdir -p /data && chown -R submitready:submitready /data /app

USER submitready
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=2)"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
