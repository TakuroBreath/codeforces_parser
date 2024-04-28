from celery import Celery
from db_work import Database
from api_work import Codeforces_API

app = Celery('tasks', broker='redis://localhost:6379/0')


@app.task
def make_request_and_fill_db():
    db = Database()
    cf = Codeforces_API()

    db.insert_problems(cf.get_problems())
    db.update_solved_count(cf.get_statistic())