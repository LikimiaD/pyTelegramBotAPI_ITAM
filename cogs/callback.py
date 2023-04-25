import re

from aiogram import Dispatcher, types, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from dataclasses import dataclass
from datetime import datetime, timedelta

from data.mongo import MongoDataBase

couples: dict = {"1": "09:00-10:35",
                 "2": "10:50-12:25",
                 "3": "12:40-14:15",
                 "4": "14:30-16:05",
                 "5": "16:20-17:55",
                 "6": "18:05-19:40",
                 "7": "19:50-21:25"}

day_to_num = {"понедельник": 0, "вторник": 1, "среду": 2, "четверг": 3, "пятницу": 4, "субботу": 5, "воскресенье": 6}

def checker(day_of_week: str) -> bool:
    today = datetime.now()
    start = today - timedelta(days=today.weekday())
    next_day = start.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=(day_to_num[day_of_week]))
    return today < next_day
    
@dataclass
class Callback:
    schedule_class: object
    bot: Bot
    db = MongoDataBase()
    state: object = None
    admin_status_buttons: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=2)
    
    def __post_init__(self):
        status = [InlineKeyboardButton("Одобрить", callback_data="adminreg_agree"),
                 InlineKeyboardButton("Отказать", callback_data="adminreg_denied"),]
        self.admin_status_buttons.add(*status)

    async def button_callback_handler(self, query: CallbackQuery):
        if query.data.lower() == 'add_name':
            await query.message.answer(text="Напишите ваше имя")
            await self.state.name.set()

        elif query.data.lower() == 'register_day':
            if query.message.text[:-4] == "Вы сейчас просматриваете расписание для кабинета:":
                await query.message.edit_text("Вы ничего не выбрали")
            else:
                cabinet = re.search(r"для кабинета: (\d+)", query.message.text).group(1)
                num_classes = re.findall(r"\d{2}:\d{2}-\d{2}:\d{2}", query.message.text)
                day_of_week = re.search(r"просматриваете (\w+),", query.message.text).group(1)
                week_type = re.search(r"(текущая|следующая) неделя", query.message.text).group(1)
                if week_type == "текущая":
                    if not checker(day_of_week):
                        await query.message.edit_text("Сорри, не можем")
                    else:
                        text = f"Вы хотите записаться в кабинет 'Г-{cabinet}',{day_of_week} на {week_type[:-2]}ей неделе.\n\nВыберите пару на которую хотите записаться."
                        markup = InlineKeyboardMarkup(row_width=7)
                        for couple, time in couples.items():
                            if time not in num_classes:
                                markup.add(InlineKeyboardButton(couple, callback_data=f"register_{couple}"))
                        await query.message.edit_text(text, reply_markup=markup)
                else:
                    text = f"Вы хотите записаться в кабинет 'Г-{cabinet}',{day_of_week} на {week_type[:-2]}ей неделе.\n\nВыберите пару на которую хотите записаться."
                    markup = InlineKeyboardMarkup(row_width=7)
                    for couple, time in couples.items():
                        if time not in num_classes:
                            markup.add(InlineKeyboardButton(couple, callback_data=f"register_{couple}"))
                    await query.message.edit_text(text, reply_markup=markup)

        else:
            func_name, data = query.data.split("_")
            if func_name.lower() == 'room':
                await self.schedule_class.show_day_keyboard(query, room = data)
                
            elif func_name == "upper":
                await self.schedule_class.show_day_keyboard(query, func_name=func_name, data=data)
                
            elif func_name == "lower":
                await self.schedule_class.show_day_keyboard(query, func_name=func_name, data=data)

            elif func_name == "register":
                cabinet = re.search(r"кабинет 'Г-(\d+)'", query.message.text).group(1)
                day_of_week = re.search(r"(понедельник|вторник|среду|четверг|пятницу|субботу|воскресенье)", query.message.text).group(1)
                week_type = re.search(r"на (\w+) неделе", query.message.text).group(1)
                week_type = "текущая неделя" if week_type == "текущей" else "следующая неделя"
                text = f"Студент с Telegram ID: {query.from_user.id} хочет записаться на {couples[data]} в кабинет 'Г-{cabinet}', {day_of_week}, {week_type}"

                self.db.add_point_to_total_user(int(query.from_user.id))
                await query.message.edit_text("Ваша заявка отправлена на рассмотрение, ожидайте ответа")

                for owner_id in self.db.grid_admins_data():
                    await self.bot.send_message(owner_id, text, reply_markup=self.admin_status_buttons)

                # text = f"В {couples[data]} мы вас ожидаем в кабинете Г-{cabinet}, {day_of_week}, {week_type}"
                
                # today = datetime.today() - timedelta(days=datetime.today().weekday())
                # day = today.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=day_to_num["вторник"])
                # self.db.register_day(query.message.from_id, str(day), couples[data])
                # await query.message.edit_text(text)
            elif func_name == "adminreg":
                id = re.search(r"Студент с Telegram ID: (\d+)", query.message.text).group(1)
                cabinet = re.search(r"кабинет 'Г-(\d+)'", query.message.text).group(1)
                day_of_week = re.search(r"(понедельник|вторник|среду|четверг|пятницу|субботу|воскресенье)", query.message.text).group(1)
                week_type = re.search(r"(\w+) неделя", query.message.text).group(1)
                pattern = re.search(r"на\s+(\d{2}:\d{2}-\d{2}:\d{2})", query.message.text).group(1)

                if data == "agree":
                    today = datetime.today() - timedelta(days=datetime.today().weekday())
                    day = today.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=day_to_num[day_of_week])
                    self.db.register_day(int(id), str(day), pattern)
                    text = f"Ваша заявка рассмотрена!\n\nМы вас ждем в {day_of_week}, {pattern}, {week_type} неделя"
                    self.db.add_point_to_accepted_user(int(id))
                else:
                    text = f"К сожалению, мы вынуждены отказать вам"
                await self.bot.send_message(id, text)
                await query.message.edit_text("Спасибо за обработку!")

    def register_handlers(self, dp: Dispatcher, state: object):
        self.state = state
        dp.register_callback_query_handler(self.button_callback_handler)