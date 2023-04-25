from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from .keyboards import Keyboard
from data.mongo import MongoDataBase

from dataclasses import dataclass

@dataclass
class User:
    keyboards = Keyboard()
    mongo = MongoDataBase()
    add_name_button = InlineKeyboardMarkup(row_width=1)
    rename_button = InlineKeyboardMarkup(row_width=1)
    state: object = None

    def __post_init__(self):
        add_name = [InlineKeyboardButton("Добавить имя", callback_data="add_name"),]
        rename = [InlineKeyboardButton("Изменить имя", callback_data="add_name"),]
        self.add_name_button.add(*add_name)
        self.rename_button.add(*rename)

    async def answer(self, message: types.Message, output: str):
        await self.keyboards.answer(message, output)

    async def welcome(self, message: types.Message):
        await self.mongo.user_data(int(message.from_id))
        await self.answer(message, "Добро пожаловать! Данный бот поможет вам легко и быстро записаться в аудиторию!")

    async def name(self, message: types.Message):
        data = message.text.split(' ')
        if len(data) == 1:
            output: str = "Введите имя\n/name {Имя}"
        else:
            output: str = data[1]
        await self.answer(message, output)
        
    async def user_information(self, message: types.Message):
        telegram_id, name, count_reg, count_visits = self.mongo.user_data(int(message.from_id))
        name_status = False
        if not name:
            name = "Имя не указано"
            name_status = True
        output = f"Ваша статистика:\n\nИмя: {name}\nВаш Telegram ID: {telegram_id}\n\nКол-во посещений: {count_visits}\nОбщее кол-во записей: {count_reg}"

        await message.answer(output, reply_markup=self.add_name_button if name_status else self.rename_button)

    async def greet_user(self, message: types.Message, state: FSMContext):
        name = message.text
        await self.answer(message, "Ваши данные обновлены" if self.mongo.add_name_to_user(message.from_id, name) else "Мы не смогли :c")
        await self.user_information(message)
        await state.finish()

    
    def register_handlers(self, dp: Dispatcher, state: object):
        self.state = state

        dp.register_message_handler(self.welcome, commands=['start', 'help'])
        dp.register_message_handler(self.name, commands=['name'])
        dp.register_message_handler(self.user_information, lambda msg: msg.text == 'Статистика')
        dp.register_message_handler(self.greet_user, state=self.state)