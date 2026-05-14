HOST="192.168.1.10"

. .venv/bin/activate

gunicorn -w 1 -b "$HOST" 'backlog_app:create_app()'
