from celery import Celery
from celery.schedules import crontab

app = Celery('tasks', broker='redis://localhost:6379/0')

app.conf.beat_schedule = {
    'make_request_every_hour': {
        'task': 'tasks.make_request_and_fill_db',
        'schedule': crontab(minute=0, hour='*'),  # Запуск каждый час
    },
}
