FROM python:3.12-slim

ARG APP_PORT=8176

ENV APP_PORT=${APP_PORT}
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.4 \
    POETRY_HOME="/opt/poetry"

ENV PATH="/root/.local/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pipx && \
    pipx ensurepath

RUN pipx install poetry==$POETRY_VERSION
RUN poetry --version

RUN useradd -m appuser

WORKDIR /app
COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi --no-root

COPY . /app
RUN poetry install --no-dev

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE ${APP_PORT}

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD curl -f http://localhost:${APP_PORT}/health || exit 1

ENV LOGURU_LEVEL=${LOGURU_LEVEL}
ENV DB_SCHEMA=${DB_SCHEMA}
ENV DB_SCHEMA_APSCHEDULER=${DB_SCHEMA_APSCHEDULER}
ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}
ENV DB_NAME=${DB_NAME}
ENV DB_USER=${DB_USER}
ENV DB_PASSWORD=${DB_PASSWORD}

CMD ["uvicorn", "job_scheduler.main:app", "--host", "0.0.0.0", "--port", "8176"]