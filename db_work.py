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

    def create_contests_table(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS contests (
                id SERIAL PRIMARY KEY,
                task_ids INTEGER[]
            );
        """)
        self.conn.commit()
        cur.close()

    def select_unique_tasks(self, points, tags):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT id FROM tasks
            WHERE points = %s AND tags && %s
            AND id NOT IN (
                SELECT UNNEST(task_ids) FROM contests
            )
            LIMIT 10;
        """, (points, tags))
        task_ids = [task[0] for task in cur.fetchall()]
        cur.close()
        return task_ids

    def create_contest(self, task_ids):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO contests (task_ids)
            VALUES (%s)
            RETURNING id;
        """, (task_ids,))
        contest_id = cur.fetchone()[0]
        self.conn.commit()
        cur.close()
        return contest_id

# def get_user_input():
#     difficulty = float(input("Введите сложность задачи: "))
#     tags = input("Введите список тем через запятую: ").split(",")
#     return difficulty, tags


# def main():
#     try:
#         conn = psycopg2.connect(
#             dbname=os.getenv("DB_NAME"),
#             user=os.getenv("DB_USER"),
#             password=os.getenv("DB_PASSWORD"),
#             host=os.getenv("DB_HOST"),
#             port=os.getenv("DB_PORT"),
#         )
#
#         create_contests_table(conn)
#
#         difficulty, tags = get_user_input()
#
#         task_ids = select_unique_tasks(conn, difficulty, tags)
#
#         contest_id = create_contest(conn, task_ids)
#
#         print(f"Создан контест с ID: {contest_id} и задачами: {task_ids}")
#
#     except Exception as e:
#         print("Ошибка:", e)
#     finally:
#         if conn is not None:
#             conn.close()
