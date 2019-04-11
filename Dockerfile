# pull official base image
FROM python:3.7-alpine

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /usr/src/app

# copy project
COPY . /usr/src/app/

# install psycopg2
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    && pip install -r requirements.txt \
    && apk del build-deps

# run entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
