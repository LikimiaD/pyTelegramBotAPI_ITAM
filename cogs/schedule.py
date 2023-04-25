from dataclasses import dataclass
from aiogram import Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from datetime import datetime

from .lk_parser import main
import re
import asyncio

days_of_week: list = ["понедельник", "вторник", "среду", "четверг", "пятницу", "субботу", "воскресенье"]

@dataclass
class Schedule:
    room_keyboard = InlineKeyboardMarkup(row_width=2)
    day_keyboard = InlineKeyboardMarkup(row_width=7)
    room_525: list = None
    room_529: list = None
    rooms: dict = None
    day: datetime = None

    def updater(self):
        self.day = datetime.today().date()
        loop = asyncio.get_event_loop()
        self.room_525, self.room_529 = loop.run_until_complete(main())

        self.rooms = {
            525: {
                "upper": self.room_525[0].main,
                "lower": self.room_525[1].main,
            },
            529: {
                "upper": self.room_529[0].main,
                "lower": self.room_529[1].main,
            }}
            
        room = [InlineKeyboardButton("525", callback_data="room_525"),
                 InlineKeyboardButton("529", callback_data="room_529")]
        
        self.room_keyboard.add(*room)

        upper = [InlineKeyboardButton("ПН", callback_data="upper_1"),
                 InlineKeyboardButton("ВТ", callback_data="upper_2"),
                 InlineKeyboardButton("СР", callback_data="upper_3"),
                 InlineKeyboardButton("ЧТ", callback_data="upper_4"),
                 InlineKeyboardButton("ПТ", callback_data="upper_5"),
                 InlineKeyboardButton("СБ", callback_data="upper_6"),
                 InlineKeyboardButton("ВС", callback_data="upper_7")]
        
        lower = [InlineKeyboardButton("ПН", callback_data="lower_1"),
                 InlineKeyboardButton("ВТ", callback_data="lower_2"),
                 InlineKeyboardButton("СР", callback_data="lower_3"),
                 InlineKeyboardButton("ЧТ", callback_data="lower_4"),
                 InlineKeyboardButton("ПТ", callback_data="lower_5"),
                 InlineKeyboardButton("СБ", callback_data="lower_6"),
                 InlineKeyboardButton("ВС", callback_data="lower_7")]
        
        self.day_keyboard.add(*upper, *lower, InlineKeyboardButton("Записаться", callback_data="register_day"))

    def __post_init__(self):
        self.updater()

    async def show_day_keyboard(self, query: CallbackQuery, func_name: str = None, data: str = None, room: str = None):
        if datetime.today().date() > self.day:
            self.updater()
        if room:
            text = f"Вы сейчас просматриваете расписание для кабинета: {room}\n\n"
        else:
            room = re.search(r'расписание для кабинета:\s*(\d+)', query.message.text).group(1)
            text = f"Вы сейчас просматриваете расписание для кабинета: {room}\n\n"
            if data != "7":
                for key, value in self.rooms[int(room)][func_name].items():
                    text += f"{key}\t{value[int(data)-1]}\n" if (value[int(data)-1]) else ""
            else:
                text += "В данный день все аудитории свободны"
            text += f'\n\nВы сейчас просматриваете {days_of_week[int(data)-1]}, {"текущая" if func_name == "upper" else "следующая"} неделя'

        await query.message.edit_text(text=text, reply_markup=self.day_keyboard)

    async def show_room_keyboard(self, query: CallbackQuery, text: str):
        await query.answer(text=text, reply_markup=self.day_keyboard)

    async def schedule(self, message: types.Message):
        await message.answer(text="Выберите комнату", reply_markup=self.room_keyboard)

    
    def register_handlers(self, dp: Dispatcher):
        dp.register_message_handler(self.schedule, lambda msg: msg.text == 'Расписание')