#!/bin/sh
set -e

# O comando 'exec' é crucial aqui. Ele substitui o processo do shell pelo
# processo do Gunicorn. Isso faz com que o Gunicorn receba os sinais do
# sistema operacional diretamente, permitindo um desligamento organizado.
exec gunicorn feira_iceflu_project.wsgi --bind 0.0.0.0:$PORT