#!/bin/sh

PISTACHIO_SETTINGS=ProdSettings pdm run gunicorn --config gunicorn.conf.py "pistachio:create_app()"
