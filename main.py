import psycopg2

from db_work import Database
from api_work import CodeforcesAPI
import os
from dotenv import load_dotenv

env_path = '.env'
load_dotenv(dotenv_path=env_path)


# db = Database()
# cf = CodeforcesAPI()
# db.create_table()
# db.insert_problems(cf.get_problems())
# db.update_solved_count(cf.get_statistic())




def create_contests_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contests (
            id SERIAL PRIMARY KEY,
            task_ids INTEGER[]
        );
    """)
    conn.commit()
    cur.close()


def get_user_input():
    difficulty = float(input("Введите сложность задачи: "))
    tags = input("Введите список тем через запятую: ").split(",")
    return difficulty, tags


def select_unique_tasks(conn, difficulty, tags):
    cur = conn.cursor()
    cur.execute("""
        SELECT id FROM tasks
        WHERE points = %s AND tags && %s
        AND id NOT IN (
            SELECT UNNEST(task_ids) FROM contests
        )
        LIMIT 10;
    """, (difficulty, tags))
    task_ids = [task[0] for task in cur.fetchall()]
    cur.close()
    return task_ids


def create_contest(conn, task_ids):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO contests (task_ids)
        VALUES (%s)
        RETURNING id;
    """, (task_ids,))
    contest_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return contest_id


def main():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )

        create_contests_table(conn)

        difficulty, tags = get_user_input()

        task_ids = select_unique_tasks(conn, difficulty, tags)

        contest_id = create_contest(conn, task_ids)

        print(f"Создан контест с ID: {contest_id} и задачами: {task_ids}")

    except Exception as e:
        print("Ошибка:", e)
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    main()

