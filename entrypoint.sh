#!/bin/sh
set -e

export DJANGO_SETTINGS_MODULE=feira_iceflu_project.settings_prod

# Adicionada a flag --timeout 120
exec gunicorn feira_iceflu_project.wsgi --bind 0.0.0.0:$PORT --timeout 120