#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset


python /app/manage.py collectstatic --noinput


/usr/local/bin/gunicorn config.asgi --bind 0.0.0.0:3000 --chdir=/app -k uvicorn.workers.UvicornWorker
