#!/bin/sh
set -e

# Diz ao Django para usar nosso novo arquivo de configurações de produção
export DJANGO_SETTINGS_MODULE=feira_iceflu_project.settings_prod

# O comando 'exec' continua o mesmo
exec gunicorn feira_iceflu_project.wsgi --bind 0.0.0.0:$PORT