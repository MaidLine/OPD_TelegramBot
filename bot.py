# -*- coding: utf-8 -*-
# Бот является модульным

from aiogram.utils import executor

from create_bot import dp
from database import SQLNotification_DB, SQLUser_DB
from handlers import client


async def on_startup(_):
    SQLNotification_DB.sql_start()
    SQLUser_DB.sql_start()
    client.start_notification_service()


# порядок импорта важен!
# аналогичную регистрацию запустить для Admin и other, когда появится там соответствующий код
client.register_handlers_client(dp)


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
