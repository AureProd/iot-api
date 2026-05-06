# --- Base image shared across stages ---
FROM python:3.12-slim AS base

# Install system dependencies
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip uninstall -y pip setuptools wheel

# Set environment variables common to all stages
# PYTHONFAULTHANDLER: print Python tracebacks on crash
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

# Change the working directory to the `app` directory
WORKDIR /app

FROM base AS builder

# Installer uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Use the system Python across both stages
ENV UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

# Copier projet et fichiers uv
COPY pyproject.toml uv.lock ./

# Installer la venv + package
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project --package iot_api

FROM builder AS dev

# Installer uv + package avec dev dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --all-groups --no-install-project --package iot_api

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

FROM base AS prod

ENV PATH="/app/.venv/bin:$PATH"

# Copier la venv buildée depuis le builder
COPY --from=builder /app/.venv ./.venv

# Copier le code source minimal pour uvicorn
COPY ./iot_api ./iot_api

EXPOSE 80

# Lancer uvicorn pour prod (pas de reload)
CMD ["/app/.venv/bin/uvicorn", "iot_api.core.app:app", "--host", "0.0.0.0", "--port", "80"]
