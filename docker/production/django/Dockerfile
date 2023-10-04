ARG DJANGO_BASE_IMAGE
ARG NODE_BASE_IMAGE

# Step 1 - Build frontend assets
FROM ${NODE_BASE_IMAGE}

WORKDIR /app

COPY ./package.json ./package-lock.json ./
COPY ./transit_odp/frontend/assets ./transit_odp/frontend/assets
COPY ./webpack ./webpack

RUN npm run build

# Step 2 - Copy frontend assets and build Django image
FROM ${DJANGO_BASE_IMAGE}

ENV PYTHONUNBUFFERED 1
ENV PATH=$PATH:/app/node_modules/.bin
WORKDIR /app

COPY --from=0 /app/transit_odp/frontend/static /app/transit_odp/frontend/static

COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install --no-dev

# Create non-privileged user
RUN addgroup django \
    && adduser -G django -D django

# Copy all the entry shell scripts to root and prepare them for use
COPY --chown=django:django \
     ./docker/production/django/gunicorn \
     ./docker/production/django/entrypoint \
     ./docker/production/django/start-migrate \
     ./docker/production/django/start-collectstatic \
     ./docker/production/django/celery/worker/start-celeryworker \
     ./docker/production/django/celery/beat/start-celerybeat \
     ./docker/production/django/celery/flower/start-celeryflower \
     /

RUN sed -i 's/\r//' /entrypoint \
    && sed -i 's/\r//' /gunicorn \
    && sed -i 's/\r//' /start-migrate \
    && sed -i 's/\r//' /start-collectstatic \
    && sed -i 's/\r//' /start-celeryworker \
    && sed -i 's/\r//' /start-celerybeat \
    && sed -i 's/\r//' /start-celeryflower \
    && chmod +x /entrypoint /gunicorn /start-migrate /start-collectstatic /start-celeryworker /start-celerybeat /start-celeryflower

# Ensure WORKDIR is owned by django user
RUN chown -R django:django /app
COPY --chown=django:django . /app

USER django

ENTRYPOINT ["/entrypoint"]
