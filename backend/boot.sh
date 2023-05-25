#!/bin/sh

# pdm run gunicorn --config gunicorn.conf.py "pistachio.app:app"
PISTACHIO_SETTINGS=ProdSettings pdm run flask --app pistachio run -h 0.0.0.0 -p 9527
