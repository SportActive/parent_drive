release: python manage.py migrate
web: python manage.py collectstatic --noinput && python manage.py migrate && gunicorn parent_drive.wsgi --bind 0.0.0.0:$PORT