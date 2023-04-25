import logging
from dataclasses import dataclass
from settings import Token

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

from cogs.user import User
from cogs.schedule import Schedule
from cogs.owner import Owner
from cogs.callback import Callback
from cogs.rights import set_admin_list

from data.mongo import MongoDataBase

@dataclass
class ITAMBot:
    token: str
    bot: Bot = None
    dp: Dispatcher = None
    db: MongoDataBase = MongoDataBase()

    class Form(StatesGroup):
        name = State()

    def __post_init__(self):
        set_admin_list(self.db.grid_admins_data())
        logging.basicConfig(level=logging.INFO)
        self.bot = Bot(token=self.token)
        storage = MemoryStorage()
        self.dp = Dispatcher(self.bot, storage=storage)

        schedule = Schedule()
        schedule.register_handlers(self.dp)

        Owner(self.bot).register_handlers(self.dp)
        User().register_handlers(self.dp, self.Form)
        Callback(schedule, self.bot).register_handlers(self.dp, self.Form)
        
    def start(self):
        executor.start_polling(self.dp, skip_updates=True)

if __name__ == "__main__":
    ITAMBot(Token.telegram.value).start()