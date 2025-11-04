# syntax=docker/dockerfile:1

# ----------------------------
# Stage 1: base python image
# ----------------------------
ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-slim-bookworm AS python

# ----------------------------
# Stage 2: build dependencies
# ----------------------------
FROM python AS builder

RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and build wheels
WORKDIR /usr/src/app
COPY ./src/app/requirements.txt ./requirements.txt
RUN pip wheel --wheel-dir /usr/src/app/wheels -r requirements.txt --no-cache-dir


# ----------------------------
# Stage 3: runtime container
# ----------------------------
FROM python AS runtime

# --- Arguments ---
ARG APP_HOME=/src/app
ARG APP_USER=fastapi
ARG APP_GROUP=fastapi

# --- Environment variables ---
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# --- Create app dir & system user (root) ---
RUN mkdir -p ${APP_HOME} \
    && groupadd -r ${APP_GROUP} || true \
    && useradd -r -g ${APP_GROUP} -d ${APP_HOME} -m ${APP_USER} || true

WORKDIR ${APP_HOME}

# --- System dependencies ---
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    sudo git bash-completion nano ssh gettext curl \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# --- Copy wheels and install packages ---
COPY --from=builder /usr/src/app/wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* \
    && rm -rf /wheels

# --- Copy application code (set ownership at copy time) ---
# NOTE: Using --chown ensures files copied from build context are owned by fastapi.
COPY --chown=${APP_USER}:${APP_GROUP} ./src/app ${APP_HOME}

# --- Copy startup scripts ---
COPY --chown=${APP_USER}:${APP_GROUP} ./docker/local/fastapi/scripts/entrypoint.sh /entrypoint.sh
COPY --chown=${APP_USER}:${APP_GROUP} ./docker/local/fastapi/scripts/start.sh /start.sh
RUN sed -i 's/\r$//g' /entrypoint.sh /start.sh \
    && chmod +x /entrypoint.sh /start.sh

# --- Logging setup (ensure correct owner after COPY) ---
RUN rm -rf ${APP_HOME}/logs \
    && mkdir -p ${APP_HOME}/logs \
    && touch ${APP_HOME}/logs/debug.log \
    && touch ${APP_HOME}/logs/error.log \
    && chown -R ${APP_USER}:${APP_GROUP} ${APP_HOME}/logs \
    && chmod -R 775 ${APP_HOME}/logs

# --- Switch to non-root user ---
USER ${APP_USER}

# --- Entrypoint ---
ENTRYPOINT ["/entrypoint.sh"]
