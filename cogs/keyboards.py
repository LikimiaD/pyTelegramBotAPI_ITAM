from aiogram import types, Bot
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from dataclasses import dataclass

from .rights import is_admin

class Keyboard():
    owner_keyboard: ReplyKeyboardMarkup = None
    user_keyboard: ReplyKeyboardMarkup = None

    def __init__(self):
        owner_lst = [KeyboardButton("Расписание", callback_data="Расписание"),
                     KeyboardButton("Статистика", callback_data="Статистика"),
                     KeyboardButton("Просмотр записей", callback_data="Просмотр записей")]

        user_lst = [KeyboardButton("Расписание", callback_data="Расписание"),
                    KeyboardButton("Статистика", callback_data="Статистика"),]

        self.owner_keyboard = ReplyKeyboardMarkup(row_width=1)
        for button in owner_lst:
            self.owner_keyboard.add(button)

        self.user_keyboard = ReplyKeyboardMarkup(row_width=1)
        for button in user_lst:
            self.user_keyboard.add(button)

    async def answer(self, message: types.Message, output: str):
        admin = is_admin(message)
        keyboard = self.owner_keyboard if admin else self.user_keyboard
        await message.answer(text=output, reply_markup=keyboard)

    async def answer_by_id(self, bot: Bot, id: int, output: str):
        admin = is_admin(None, id)
        keyboard = self.owner_keyboard if admin else self.user_keyboard
        await bot.send_message(chat_id=id, text=output, reply_markup=keyboard)
