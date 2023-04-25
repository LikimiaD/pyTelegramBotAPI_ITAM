from dataclasses import dataclass

from aiogram import Dispatcher, types

from .keyboards import Keyboard
from data.mongo import MongoDataBase

from .rights import is_admin, admin_only, set_admin_list


@dataclass
class Owner:
    bot: object
    keyboards = Keyboard()
    db = MongoDataBase()

    async def answer(self, message: types.Message, output: str):
        await self.keyboards.answer(message, output)

    async def days_information(self, message: types.Message):
        text: str = self.db.get_records_between_dates()
        await self.answer(message, text)

    @admin_only
    async def add_owner(self, message: types.Message):
        _, data = message.text.split()
        self.db.add_in_admins_data(int(data))
        set_admin_list(self.db.grid_admins_data())
        await self.keyboards.answer_by_id(self.bot, int(data), "Вы теперь администратор!")
    
    def register_handlers(self, dp: Dispatcher):
        dp.register_message_handler(self.days_information,  lambda msg: msg.text == 'Просмотр записей' and is_admin(msg))
        dp.register_message_handler(self.add_owner,  commands=['add_owner'])