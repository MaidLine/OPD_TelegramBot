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
    base.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY, user_id INTEGER NOT NULL, date TEXT NOT NULL, text TEXT NOT NULL)')
    base.commit()


async def sql_add_to_db(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO users (user_id, date, text) VALUES (?, ?, ?)', tuple(data.values()))
        base.commit()


def get_time(user_id):
    dt = cur.execute(f'SELECT date FROM users WHERE user_id = {user_id}').fetchall()
    base.commit()
    return dt


def get_text(user_id, date):
    textlist = cur.execute(f"SELECT text FROM users WHERE user_id = {user_id} AND date = '{date}'").fetchall()
    texttuple = textlist[0]
    text = texttuple[0]
    base.commit()
    return text


def get_notify_list(): # получения списка неповторяющихся айдишников
    list = cur.execute('SELECT DISTINCT user_id FROM users').fetchall()
    base.commit()
    return list


def delete_notyfied_user(user_id, date): # удаляет из бд оповещенного пользователя
    cur.execute(f"DELETE FROM users WHERE user_id ={user_id} AND date ='{date}'")
    base.commit()
    return base
