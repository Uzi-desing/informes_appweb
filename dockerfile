# ── Etapa 1: compilar Tailwind CSS ──
FROM node:22-slim AS css
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY src/ src/
RUN npx @tailwindcss/cli \
      -i ./src/static_dev/css/tailwind.input.css \
      -o ./src/static/css/tailwind.css \
      --minify

# ── Etapa 2: instalar Python deps + collectstatic ──
FROM python:3.14-slim AS builder
RUN pip install --no-cache-dir uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src/ src/
COPY --from=css /app/src/static/css/tailwind.css src/static/css/tailwind.css
RUN uv sync --frozen --no-dev
# Build con DEBUG=False (necesario para que WhiteNoise comprima/hashee los
# estáticos). El chequeo de seguridad de settings.py se omite durante
# collectstatic; el SECRET_KEY real lo inyecta el secret manager en runtime.
ENV DEBUG="False"
RUN .venv/bin/python src/manage.py collectstatic --noinput

# ── Etapa 3: imagen final ──
FROM python:3.14-slim
RUN groupadd -r appuser && useradd -g appuser appuser
ENV HOME=/app
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings \
    PATH="/app/.venv/bin:$PATH"
COPY --from=builder /app/.venv .venv/
COPY --from=builder /app/src ./
RUN chown -R appuser:appuser /app
EXPOSE 8000
USER appuser
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "120", "--workers", "2", "config.wsgi:application"]
