web: gunicorn mlpulse.wsgi:application
worker: celery -A mlpulse worker --loglevel=info
beat: celery -A mlpulse beat --loglevel=info -S django_celery_beat.schedulers:DatabaseScheduler
