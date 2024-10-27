FROM python:3.11-slim
LABEL authors="valiaisnotprogrammer"
ENV APP_DIR="/opt/discount"
ENV APP_USER=app
ENV POETRY_VERSION=1.8.3

RUN mkdir -p ${APP_DIR} \
  && useradd -s /bin/bash -u 1000 -d ${APP_DIR} ${APP_USER} \
  && chown -R ${APP_USER} ${APP_DIR} \
  && chmod 700 ${APP_DIR}

WORKDIR $APP_DIR

RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

COPY pyproject.toml poetry.lock ./
COPY --chown=${APP_USER}:${APP_USER} . ${APP_DIR}

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

USER ${APP_USER}

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "${RUN__HOST}", "--port", "${RUN_PORT}"]