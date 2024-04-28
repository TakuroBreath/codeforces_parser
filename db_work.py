import psycopg2
import os
from dotenv import load_dotenv

env_path = '.env'
load_dotenv(dotenv_path=env_path)


class Database:
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )

    def create_table(self):
        # Создание таблицы tasks
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                contestId INTEGER,
                problemsetName TEXT,
                index TEXT,
                name TEXT,
                task_type TEXT CHECK (task_type IN ('PROGRAMMING', 'QUESTION')),
                points FLOAT,
                rating INTEGER,
                tags TEXT[],
                solvedCount INTEGER
            )
        """)

        try:
            cur.execute("CREATE UNIQUE INDEX idx_unique_contestid_index ON tasks (contestid, index);")
        except Exception as e:
            print(e)

        self.conn.commit()
        cur.close()

    def insert_problems(self, problems):
        cur = self.conn.cursor()
        for problem in problems:
            cur.execute("""
                        INSERT INTO tasks (contestId, problemsetname, index, name, task_type, points, rating, tags)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (contestid, index) DO UPDATE
                        SET 
                            problemsetname = excluded.problemsetname,
                            name = excluded.name,
                            task_type = excluded.task_type,
                            points = excluded.points,
                            rating = excluded.rating,
                            tags = excluded.tags
                    """, (
                problem.get('contestId'),
                problem.get('problemsetName'),
                problem.get('index'),
                problem.get('name'),
                problem.get('type'),
                problem.get('points'),
                problem.get('rating'),
                problem.get('tags')
            ))
        self.conn.commit()
        cur.close()

    def update_solved_count(self, problem_statistic):
        cur = self.conn.cursor()
        for problem_stat in problem_statistic:
            cur.execute("""
                UPDATE tasks
                SET solvedCount = %s
                WHERE contestId = %s AND index = %s
            """, (
                problem_stat.get('solvedCount'),
                problem_stat.get('contestId'),
                problem_stat.get('index')
            ))
        self.conn.commit()
        cur.close()
