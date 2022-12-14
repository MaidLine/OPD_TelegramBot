import sqlite3
from sqlite3 import Error


def sql_start():
    global base, cur
    try:
        base = sqlite3.connect('sql3_BotDB.db')
        print('Подключение к БД успешно')
    except Error as e:
        print(f'BD error: {e}')
    cur = base.cursor()
    base.execute('CREATE TABLE IF NOT EXISTS students (id INTEGER NOT NULL PRIMARY KEY,user_id INTEGER NOT NULL, ingroup STRING NOT NULL, faculty STRING NOT NULL)')
    base.execute('CREATE TABLE IF NOT EXISTS teachers (id INTEGER NOT NULL PRIMARY KEY, name STRING NOT NULL, secondname STRING NOT NULL)')
    base.commit()


async def sql_add_to_db(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO students (user_id, ingroup, faculty) VALUES (?, ?, ?)', tuple(data.values()))
        base.commit()


def get_data(user_id):
    data = cur.execute(f'SELECT * FROM students WHERE user_id = {user_id}').fetchone()
    base.commit()
    return data


def check_is_exist(user_id):
    bool = cur.execute(f'SELECT * FROM students WHERE user_id = {user_id}').fetchone()
    if bool == None:
        return False
    else:
        return True


def delete_user(data):
    cur.execute(f"DELETE FROM students WHERE user_id = {data[1]} AND ingroup = '{data[2]}' AND faculty = '{data[3]}'")
    base.commit()

