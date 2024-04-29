from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

from api_work import CodeforcesAPI
from db_work import Database

env_path = '.env'
load_dotenv(dotenv_path=env_path)

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')

CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'

app = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_BROKER_URL)

schedule = crontab(minute=0, hour='*')


@app.task
def fetch_database():
    cf = CodeforcesAPI()
    db = Database()
    problems = cf.get_problems()
    statistics = cf.get_statistic()

    db.insert_problems(problems)
    db.update_solved_count(statistics)


app.conf.beat_schedule = {
    'fetch_db': {
        'task': 'tasks.fetch_database',
        'schedule': schedule,
    },
}
