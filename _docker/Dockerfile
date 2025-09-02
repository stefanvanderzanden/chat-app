# --------------------------
# STAGE 1: base builder
# --------------------------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/usr/local

# Nodig voor het bouwen van wheels
RUN apt-get update && apt-get install --no-install-recommends -y \
    curl libpq-dev python3-dev build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Alleen dependency-files eerst (cache-laag!)
COPY pyproject.toml uv.lock ./

# Installeer dependencies in een eigen virtuele omgeving
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# Copy source
COPY src ./src

# Installeer project in omgeving
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# --------------------------
# STAGE 2: runtime image
# --------------------------
FROM python:3.12-slim AS runtime

ENV USER=app-user \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Alleen minimale runtime deps
RUN apt-get update && apt-get install --no-install-recommends -y \
    libpq5 curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash $USER

WORKDIR /home/$USER/app

# Kopieer alleen geïnstalleerde packages uit de builder
COPY --from=builder /usr/local /usr/local

# Kopieer de projectcode
COPY --from=builder /app/src /home/$USER/app
RUN mkdir -p /home/$USER/app/staticfiles /home/$USER/app/media

# Ownership fix
RUN chown -R "$USER":"$USER" /home/$USER/app
USER $USER

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
