from aiogram import types
from aiogram.types import ReplyKeyboardMarkup


notificationbutton = types.KeyboardButton('/notification')
sheldurebutton = types.KeyboardButton('/sheldure')
questionsbutton = types.KeyboardButton('/FAQ')
registrationbutton = types.KeyboardButton('/registration')
cancelbutton = types.KeyboardButton('/cancel')
resetregbutton = types.KeyboardButton('/reset_reg')


kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
kb_registationuser = ReplyKeyboardMarkup(resize_keyboard=True)
kb_cancel = ReplyKeyboardMarkup(resize_keyboard=True)


kb_client.add(notificationbutton).insert(sheldurebutton).add(questionsbutton).insert(registrationbutton).insert(resetregbutton)
kb_registationuser.add(registrationbutton)
kb_cancel.add(cancelbutton)
