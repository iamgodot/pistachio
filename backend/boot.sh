#!/bin/sh

# pdm run gunicorn --config gunicorn.conf.py "pistachio.app:app"
pdm run flask --app pistachio run -h 0.0.0.0 -p 9527
