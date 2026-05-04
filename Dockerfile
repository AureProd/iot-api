# Certificate Generation ---
FROM alpine:latest AS cert-gen

RUN apk add --no-cache openssl

WORKDIR /certs

# Generate private key (RS256) and public key certs
RUN openssl genrsa -out private.pem 2048 && \
    openssl rsa -in private.pem -pubout -out public.pem

FROM python:3.12-slim AS builder

# Installer uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Use the system Python across both stages
ENV UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

# Change the working directory to the `app` directory
WORKDIR /app

# Copier projet et fichiers uv
COPY pyproject.toml uv.lock ./

# Installer la venv + package
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project --package iot_api

FROM builder AS dev

# Installer uv + package avec dev dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --all-groups --no-install-project --package iot_api

COPY --from=cert-gen /certs /app/certs

# Dev environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    APP_DEBUG=1 \
    PYDEVD_DISABLE_FILE_VALIDATION=1 \
    UV_NO_SYNC=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONOPTIMIZE=1

EXPOSE 80

# Lancer uvicorn avec hot reload
CMD ["/app/.venv/bin/uvicorn", "iot_api.core.app:app", "--host", "0.0.0.0", "--port", "80", "--reload"]

FROM python:3.12-slim

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

# Copier la venv buildée depuis le builder
COPY --from=builder /app/.venv ./.venv

# Copier le code source minimal pour uvicorn
COPY ./iot_api ./iot_api

COPY --from=cert-gen /certs /app/certs

EXPOSE 80

# Lancer uvicorn pour prod (pas de reload)
CMD ["/app/.venv/bin/uvicorn", "iot_api.core.app:app", "--host", "0.0.0.0", "--port", "80"]