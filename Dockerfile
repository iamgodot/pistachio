FROM python:3.11-slim

# Without this editable install will get stuck
WORKDIR /app

COPY . .
# Pre-installation for mysqlclient
RUN apt-get update && apt-get install -y python3-dev default-libmysqlclient-dev build-essential pkg-config && pip install pdm && pdm install

EXPOSE 9527
CMD make run
