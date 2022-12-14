# данный файл нужен во избежание ошибки циклической загрузки
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher

storage = MemoryStorage()

# создаются экземпляры бота
bot = Bot(token='5411480652:AAGB4JJGkqD0UOZyYz9o9N4-MpKEykZrwZ0')
dp = Dispatcher(bot, storage=storage)
