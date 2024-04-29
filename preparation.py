from db_work import Database

# Подключение к БД
db = Database()

# Создание таблицы с заданиями
db.create_table()

# Создание таблицы с контестами
db.create_contests_table()
