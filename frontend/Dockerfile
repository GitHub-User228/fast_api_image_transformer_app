FROM python:3.10.14-slim

WORKDIR /app

COPY requirements.txt requirements.txt
COPY env/.env env/.env

RUN sed -e 's/^/export /' env/.env >> ~/.bashrc && \
    . ~/.bashrc && \
    pip install pip --upgrade && \
    pip install --no-cache-dir --upgrade -r requirements.txt

COPY scripts scripts

RUN chmod +x scripts/entrypoint.sh

ENTRYPOINT ["/bin/bash", "scripts/entrypoint.sh"]