FROM python:3.11-slim

# Without this editable install will get stuck
WORKDIR /app

COPY . .
RUN pip install pdm && pdm install

EXPOSE 9527
CMD ./boot.sh
