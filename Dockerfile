# Stage 1: init
FROM python:3.12 AS init

ARG uv=/root/.local/bin/uv

# Install `uv` for faster package bootstrapping
ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh

# Copy local context to `/app` inside container (see .dockerignore)
WORKDIR /app
COPY . .
RUN mkdir -p /app/data /app/uploaded_files

# Create virtualenv which will be copied into final container
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN $uv venv

# Install app requirements and reflex inside virtualenv
RUN $uv sync

# Deploy templates and prepare app
RUN reflex init

# Export static copy of frontend to /app/.web/_static
RUN reflex export --frontend-only --no-zip

# Copy static files out of .web and remove .web
RUN mv .web/_static /tmp/_static
RUN rm -rf .web && mkdir .web
RUN mv /tmp/_static .web/_static


# Stage 2: copy artifacts into slim image
FROM python:3.12-slim

# Copy artifacts from init stage
WORKDIR /app
RUN adduser --disabled-password --home /app reflex
COPY --chown=reflex --from=init /app /app

# Install redis-server
RUN chown -R reflex:reflex /app && \
    apt-get update && apt-get install -y curl redis-server unzip && \
    rm -rf /var/lib/apt/lists/*
USER reflex

# Set user and environment variables
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1

# Needed until Reflex properly passes SIGTERM on backend.
STOPSIGNAL SIGKILL

# Always apply migrations before starting the backend.
CMD ["sh", "-c", "[ -d alembic ] && reflex db migrate; redis-server --daemonize yes && exec reflex run --env prod"]
