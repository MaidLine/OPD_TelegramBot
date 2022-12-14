# -*- coding: utf-8 -*-
import asyncio
import requests

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from create_bot import bot
from database import SQLNotification_DB, SQLUser_DB
from keyboards import kb_client, kb_registationuser, kb_cancel
from aiogram import Dispatcher, types


# @dp.message_handler(commands=['start', 'help'])
async def start(message):
    await message.reply(f'Привет, {message.from_user.first_name}', reply_markup=kb_client)


async def FAQ(message):
    # бот может отсылать в секунду до 30 сообщений (ограничение телеги),
    # поэтому если будет больше 20 сообщений, надо добавить await asyncio.sleep(1)
    await message.reply('Зачёт можно получить автоматом, если сам преподаватель сочтёт это возможным. Официально ничего'
                        ' не закреплено, и в этом случае необходимо, чтобы преподаватель вас отметил для себя как'
                        ' старательного и добросовестного студента. Субъективное мнение будет играть весомую роль,'
                        ' порой даже большее, чем все учебные заслуги.')
    await message.reply('«Автомат» как форма оценки знаний должен быть отмечен в «Положениях о зачётах и экзаменах»'
                        ' учебного учреждения, прописаны конкретные критерии, которым надо соответствовать, чтобы вам'
                        ' оценку ставили автоматически. Выполняете все требования — получаете «автомат» по учебной'
                        ' дисциплине.')


async def reset_registration(message):
    data = SQLUser_DB.get_data(message.from_user.id)
    if data == None:
        await message.reply('Вы не зарегистрированы')
    else:
        SQLUser_DB.delete_user(data)
        await message.reply('Успешно')


async def sheldure(message):
    datas = SQLUser_DB.get_data(message.from_user.id)
    if datas == None:
        await message.reply('Вам нужно зарегистрироваться, чтобы можно было получать расписание',
                            reply_markup=kb_registationuser)
    else:
        await message.reply('Это займет несколько секунд')
        group = datas[2]
        facultet = datas[3]
        if get_html(URL + str(facultet) + '/groups/' + str(group)).status_code == 200:
            html = get_html(URL + str(facultet) + '/groups/' + str(group))
            par, m = get_content(html.text)
            if m > 0:
                out(par, m)
                with open(r"test.txt", "r") as file:
                    mess = file.read()
                await bot.send_message(message.chat.id, f'Твое расписание на сегодня: ', parse_mode='html')
                await bot.send_message(message.chat.id, mess, parse_mode='html')
            else:
                await bot.send_message(message.chat.id, f'Сегодня пар нет!', parse_mode='html')
        else:
            await bot.send_message(message.chat.id, f'Настройки установлены неверно. Для смены настроек введи /settings',
                             parse_mode='html')


HOST = "https://timetable.tusur.ru/"
URL = 'https://timetable.tusur.ru/faculties/'
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.35'
    }


def get_html(url, params=''):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    par = []
    m = 0
    now = datetime.now()
    sep = datetime(now.year if now.month >= 9 else now.year - 1, 9, 1)
    d1 = sep - timedelta(days=sep.weekday())
    d2 = now - timedelta(days=now.weekday())
    parity = ((d2 - d1).days // 7) % 2
    week = format("even" if parity else "odd")
    for n in range(0, 7):
        items = soup.find(class_="table table-bordered table-condensed hidden-xs hidden-sm table-lessons " + week).find_all('td', class_='lesson_cell day_'+ str(n)+' current_day')
        for item in items:
            if item.find('h4') is not None:
                par.append(
                    {
                    'lessons_nazvinie':item.find('div', class_='modal-header').find('h4').get_text(' ', strip=True),
                    'lessons_time':item.find('div', class_='modal-content').find('p').find_next('p').find_next('p').get_text(' ', strip=True),
                    'lessons_vid':item.find('div', class_='modal-content').find('p').get_text(' ', strip=True),
                    'lessons_mesto':item.find('div', class_='modal-content').find('p').find_next('p').find_next('p').find_next('p').get_text(' ', strip=True),
                    'lessons_teacher':item.find('div', class_='modal-content').find('p').find_next('p').find_next('p').find_next('p').find_next('p').get_text(' ', strip=True),
                    'lessons_group':item.find('div', class_='modal-content').find('p').find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').get_text(' ', strip=True),
                    }
                )
                m+=1
    return par, m


def out(par, m):
    with open(r"test.txt", "w") as file:
        for n in range(0, m):
            for value in list(par[n].values()):
                file.write(value + '\n')
            file.write('\n')


# это машина состояний, аналог register_next_step в telebot
class FSMSheldure(StatesGroup):
    group = State()
    faculty = State()


async def registration(message: types.Message):
    if SQLUser_DB.check_is_exist(message.from_user.id) == True:
        await message.reply('Вы уже зарегистрированы')
    else:
        await FSMSheldure.group.set()
        await message.reply('Введите номер вашей группы (в формате 111-1, v-11b, 111-m и тд).', reply_markup=kb_cancel)


async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await message.reply('Отмена ввода', reply_markup=kb_client)
    await state.finish()


async def save_group(message, state: FSMContext):
    async with state.proxy() as data:
        data['user_id'] = message.from_user.id
        data['group'] = message.text.lower()
    await FSMSheldure.next()
    await message.reply('Введите ваш факультет (в формате rtf, fvs, fet, ef, yuf, zivf, rkf, fsu, fit, gf, fb).')


async def save_faculty(message, state: FSMContext):
    async with state.proxy() as data:
        data['faculty'] = message.text.lower()
    await SQLUser_DB.sql_add_to_db(state)
    await state.finish()
    await message.reply('Данные сохранены!', reply_markup=kb_client)


class FSMNotifer(StatesGroup):
    dt = State()
    text = State()


# @dp.message_handler(commands=['notification'])
async def notification(message: types.Message):
    await FSMNotifer.dt.set()
    await message.reply('Введите дату напоминания в формате YYYY-MM-DD HH:MM:SS', reply_markup=kb_cancel)


async def save_id_and_time(message, state: FSMContext):
    async with state.proxy() as data:
        data['user_id'] = message.from_user.id
        data['date'] = message.text
    await FSMNotifer.next()
    await message.reply('Введите текст напоминания')


async def save_text(message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
    await SQLNotification_DB.sql_add_to_db(state)
    create_notify_task(data['user_id'], data['date'])
    # до этого метода нужно делать все дела с данными, после него данные из памяти стираются
    await state.finish()
    await message.reply('Оповещение сохранено!', reply_markup=kb_client)


def start_notification_service():
    global setloop
    setloop = set()
    id_list = SQLNotification_DB.get_notify_list() # результат получения - список, в котором кортеж значения в str формате
    for user in id_list:
        date_list = SQLNotification_DB.get_time(user[0])
        for date in date_list:
            create_notify_task(user[0], date[0])


def create_notify_task(user_id, date):
    loop = asyncio.get_event_loop()
    loop.create_task(check(user_id, date), name=f'{user_id}')
    setloop.add(loop)


# я знаю, что здесь ошибка, так надо)
async def check(user_id, date):
    if len(date) == 13:
        dateofnotify = datetime.strptime(date, '%Y-%m-%d %H')
    elif len(date) == 16:
        dateofnotify = datetime.strptime(date, '%Y-%m-%d %H:%M')
    elif len(date) == 19:
        dateofnotify = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    while True:
        now = datetime.now()
        if dateofnotify <= now:
            text = SQLNotification_DB.get_text(int(user_id), date)
            await bot.send_message(int(user_id), text)
            break
        await asyncio.sleep(60)
    SQLNotification_DB.delete_notyfied_user(user_id, date)


# данная функция регистрирует хэндлеры для отправки в bot.py
def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start', 'help'])
    dp.register_message_handler(notification, commands=['notification'])
    dp.register_message_handler(sheldure, commands=['sheldure'])
    dp.register_message_handler(registration, commands=['registration'])
    dp.register_message_handler(FAQ, commands=['FAQ'])
    dp.register_message_handler(reset_registration, commands=['reset_reg'])
    # хэндлер функции отмены должен идти раньше всех функций, связанных с машиной состояний, чтобы можно было отменять
    # ввод и останавливать машину состояний
    dp.register_message_handler(cancel_handler, commands=['cancel'], state='*')
    dp.register_message_handler(save_group, state=FSMSheldure.group)
    dp.register_message_handler(save_faculty, state=FSMSheldure.faculty)
    dp.register_message_handler(save_id_and_time, state=FSMNotifer.dt)
    dp.register_message_handler(save_text, state=FSMNotifer.text)
