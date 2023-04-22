from os import environ

from dotenv import dotenv_values

configs = {**dotenv_values(".env"), **environ}

# Debugging
reload = configs.get("GUNICORN_RELOAD", False)

# Logging
# accesslog = '-'
# errorlog = '-'
loglevel = "info"
# logconfig_dict = {}

# Server mechanics
# preload_app = False
# sendfile = None
# reuse_port = False
# daemon = False

# Server socket
bind = configs.get("GUNICORN_BIND", "0.0.0.0:9527")
# backlog = 2048

# Worker processes
workers = configs.get("GUNICORN_WORKERS", 3)
worker_class = configs.get("GUNICORN_WORKER_CLASS", "gevent")
# threads = 1
# worker_connections = 1000
# max_requests = 0
# max_requests_jitter = 0
# timeout = 30
# graceful_timeout = 30
# keepalive = 2
