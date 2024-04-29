from datetime import datetime

from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

from api_work import CodeforcesAPI  # Подключите модуль для работы с API
from db_work import Database  # Подключите модуль для работы с базой данных

env_path = '.env'
load_dotenv(dotenv_path=env_path)

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')

CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'

app = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_BROKER_URL)

# Определяем периодическое расписание (например, каждый час)
schedule = crontab()


# Определяем периодическую задачу
@app.task()
def fetch_and_fill_database():
    cf = CodeforcesAPI()
    db = Database()
    # Выполняем запрос к API
    problems = cf.get_problems()
    statistics = cf.get_statistic()

    # Заполняем базу данных
    db.insert_problems(problems)
    db.update_solved_count(statistics)


# Указываем задачу в настройках beat_schedule для Celery Beat
app.conf.beat_schedule = {
    'fetch_db': {
        'task': 'tasks.fetch_and_fill_database',
        'schedule': 60,
    },
}
