from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

env_path = '.env'
load_dotenv(dotenv_path=env_path)

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')

CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}'

app = Celery('tasks', broker=CELERY_BROKER_URL)

app.conf.beat_schedule = {
    'make_request_every_hour': {
        'task': 'tasks.make_request_and_fill_db',
        'schedule': crontab(minute=0, hour='*'),  # Запуск каждый час
    },
}
