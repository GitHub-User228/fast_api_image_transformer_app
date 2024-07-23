FROM python:3.10.14-slim

USER root

WORKDIR /home/fast_api_app

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1-mesa-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY env/.env env/.env

RUN sed -e 's/^/export /' env/.env >> ~/.bashrc && \
    . ~/.bashrc && \
    pip install pip --upgrade && \
    pip install --no-cache-dir --upgrade -r requirements.txt

COPY scripts scripts

RUN chmod +x scripts/entrypoint.sh

ENTRYPOINT ["/bin/bash", "scripts/entrypoint.sh"]