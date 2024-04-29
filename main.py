import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import os
from dotenv import load_dotenv
from db_work import Database

env_path = '.env'
load_dotenv(dotenv_path=env_path)

# Апи токен для бота телеграм
API_TOKEN = os.getenv('API_TOKEN')

# Уровень логирования при запуске
logging.basicConfig(level=logging.INFO)

# Создание экземпляра бота и диспетчера для обработки
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# База данных
db = Database()

# Функция для обработки команды /start
@dp.message(Command("start"))
async def start(message: types.Message):
    msg = """
    Приветствую тебя в боте, предназначенном для получения и поиска задач с Codeforces!
    
    Для повторного получения информации введи "/start"
    Для поиска задачи воспользуйся конструкцией "/search contestId index", 
    где contestId - номер соревнования, index - индекс задачи в контесте
    для теста можно использовать например 1966 A
    
    Для получения персонализированного контеста из 10 задач, отправь в чат сообщение в формате:
    "theme1,theme2,points", например, greedy,1000
    Можешь искать несколько тем сразу, а можешь лишь одну.
    В качестве количества очков используй целое число от 250 до 6000 с шагом 250 (250, 500, 750, 1000, etc)
    """
    await message.answer(msg)


# Функция для обработки команды /search
@dp.message(Command("search"))
async def search(message: types.Message):
    text = message.text
    msg = ""
    try:
        contest_id, index = text.replace('/search', '').split()
        contest_id = int(contest_id)
        index = index.upper()
        task = db.find_task_by_contest_id_and_index(contest_id, index)

        msg = f"""
                Задача, которую вы искали:
                
                Темы: {', '.join(i for i in task['tags'])}
                Решено раз: {task['solvedCount']}
                Номер задачи и название: {task['contestId']}{task['index']} {task['name']}
                Сложность задачи: {task['points']}
        """

    except ValueError:
        msg = 'Пожалуйста, укажите корректные данные для поиска. Для справки нажми: "/start"'

    await message.answer(msg)


# Обработчик для всех сообщений
@dp.message()
async def process_contest(message: types.Message):
    try:
        text = message.text
        if text.startswith('/start'):
            return await start(message)
        if text.startswith('/search'):
            return await search(message)

        tags = text.split(",")
        points = int(tags.pop())

        unique_tasks = db.select_unique_tasks(points, tags)

        db.create_contest(unique_tasks)
        tasks = db.fetch_tasks_by_ids(unique_tasks)

        msg = ""
        counter = 0
        for task in tasks:
            counter += 1
            msg = f"""
            Задача из подборки №{counter}
            
            Темы: {', '.join(i for i in task['tags'])}
            Решено раз: {task['solvedCount']}
            Номер задачи и название: {task['contestId']}{task['index']} {task['name']}
            Сложность задачи: {task['points']}
            """

            await message.answer(msg)

    except Exception as e:
        await message.answer(f"Кажется, что-то пошло не так. \n Вот причина: {e}")


# Запуск опроса
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Асинхронный запуск опрашивающей функции
    asyncio.run(main())
