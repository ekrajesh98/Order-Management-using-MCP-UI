FROM python:3.13-slim

ENV APP_LOG_LEVEL=info
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV APP_PORT=8501

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openssl \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry

RUN python -m venv "/opt/venv" \
    && . "/opt/venv/bin/activate" \
    && pip install --upgrade --no-cache-dir pip setuptools

COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false \
    && poetry install

RUN apt-get autoremove && \
    rm -fr /var/lib/apt/lists/{apt,dpkg,cache,log} /tmp/* /var/tmp/*

RUN mkdir -p /app/.streamlit

COPY src/ /app/src/
COPY .streamlit /app/.streamlit/
COPY app_start.sh /app/


EXPOSE ${APP_PORT}
RUN chmod a+x /app/app_start.sh

CMD ["/app/app_start.sh"]
