FROM python:3.6-alpine

RUN apk update \
    && \
    apk add \
      build-base \
      libpq \
      postgresql-dev \
    && \
    pip install --upgrade pip \
    && \
    pip install -r requirements.txt

WORKDIR /var/www/site
ENTRYPOINT ['python']
CMD ['run.py']
