FROM python:3.14-slim AS builder

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src/ src/
RUN uv sync --frozen --no-dev

RUN .venv/bin/python src/manage.py collectstatic --noinput


FROM python:3.14-slim

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings \
    PATH="/app/.venv/bin/$PATH"
    
COPY --from=builder /app/.venv .venv/
COPY --from=builder /app/src ./
COPY --from=builder /app/staticfiles staticfiles/

RUN chown -R appuser:appuser /app

EXPOSE 8000

USER appuser

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]