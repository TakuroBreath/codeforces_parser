import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, ARRAY, func, UniqueConstraint
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.schema import CheckConstraint

env_path = '.env'
load_dotenv(dotenv_path=env_path)

engine = create_engine(os.getenv("DATABASE_URL"))
Base = declarative_base()


class Task(Base):
    """Модель таблицы заданий"""
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    contestId = Column(Integer)
    problemsetName = Column(String)
    index = Column(String)
    name = Column(String)
    task_type = Column(String, CheckConstraint("task_type IN ('PROGRAMMING', 'QUESTION')"))
    points = Column(Float)
    rating = Column(Integer)
    tags = Column(ARRAY(String))
    solvedCount = Column(Integer)

    __table_args__ = (
        UniqueConstraint('contestId', 'index'),
    )


class Contest(Base):
    """Модель таблицы контестов"""
    __tablename__ = 'contests'

    id = Column(Integer, primary_key=True)
    task_ids = Column(ARRAY(Integer))


class Database:
    """Класс базы данных"""

    def __init__(self):
        engine = create_engine(os.getenv("DATABASE_URL"))
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def create_table(self):
        """Создание таблиц"""
        Base.metadata.create_all(engine)

    def insert_problems(self, problems):
        """Заполнение таблицы с заданиями"""
        tasks = []
        for problem in problems:
            task = Task(
                contestId=problem.get('contestId'),
                problemsetName=problem.get('problemsetName'),
                index=problem.get('index'),
                name=problem.get('name'),
                task_type=problem.get('type'),
                points=problem.get('points'),
                rating=problem.get('rating'),
                tags=problem.get('tags')
            )
            tasks.append(task)

        try:
            self.session.bulk_save_objects(tasks)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()

        self.session.close()

    def update_solved_count(self, problem_statistic):
        """Добавление в таблицу количество решений для задач"""
        for stat in problem_statistic:
            self.session.query(Task).filter_by(contestId=stat['contestId'], index=stat['index']).update(
                {'solvedCount': stat['solvedCount']}
            )
        self.session.commit()

    def create_contests_table(self):
        """Создание таблицы с контестами"""
        Base.metadata.create_all(engine)

    def select_unique_tasks(self, points, tags):
        """Функция для выбора уникальных заданий"""
        subquery = self.session.query(func.unnest(Contest.task_ids)).subquery()

        task_ids = self.session.query(Task.id). \
            filter(Task.points == points). \
            filter(func.array_to_string(Task.tags, ',').like(f'%{",".join(tags)}%')). \
            filter(~Task.id.in_(subquery)). \
            limit(10).all()

        task_ids = [task_id for task_id, in task_ids]

        return task_ids

    def create_contest(self, task_ids):
        """Создание контеста"""
        contest = Contest(task_ids=task_ids)
        self.session.add(contest)
        self.session.commit()
        return contest.id

    def fetch_tasks_by_ids(self, task_ids):
        """Выборка заданий по их номеру"""
        tasks = self.session.query(Task).filter(Task.id.in_(task_ids)).all()
        return [task.__dict__ for task in tasks]

    def find_task_by_contest_id_and_index(self, contest_id, index):
        """Поиск задания по номеру и индексу"""
        task = self.session.query(Task).filter_by(contestId=contest_id, index=index).first()
        return task.__dict__ if task else None


def format_task(task):
    task_dict = {
        'id': task[0],
        'contestId': task[1],
        'problemsetName': task[2],
        'index': task[3],
        'name': task[4],
        'task_type': task[5],
        'points': task[6],
        'rating': task[7],
        'tags': task[8],
        'solvedCount': task[9]
    }

    return task_dict
