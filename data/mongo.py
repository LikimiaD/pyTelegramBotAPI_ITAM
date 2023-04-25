import pymongo
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo import MongoClient

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from settings import Checker

from datetime import datetime, timedelta

from dataclasses import dataclass

class MongoDataBase:
    client: MongoClient = pymongo.MongoClient("mongodb://localhost:27017")
    db: Database = client.telegram_itam
    users: Collection = db.users
    days: Collection = db.days
    admins: Collection = db.admins

    def user_data(self, telegram_id: int) -> tuple:
        """
        Проверка на наличие аккаунта в ДБ

        Автоматически добавит если нету

        >>> INPUT: user_data(telegram_id: int)
        >>> OUTPUT: telegram_id, name, count_reg, count_visits
        """
        data: dict = self.users.find_one(
            {"telegram_id": telegram_id})
        
        if data:
            name = data.get("name")
            count_reg = data.get("count_reg")
            count_visits = data.get("count_visits")
            return telegram_id, name, count_reg, count_visits
        else:
            self.users.insert_one(
                {"telegram_id": telegram_id, "name": None, "count_reg": 0, "count_visits": 0 }
            )
            return telegram_id, None, 0, 0
        
    def add_name_to_user(self, telegram_id: int, name: str) -> bool:
        """
        Добавляет\Изменяет имя пользователя

        >>> INPUT: add_name_to_user(telegram_id: int, name: str)
        >>> OUTPUT: True - выполнилось, False - не смогло
        """
        try:
            self.users.update_one(
                {"telegram_id": telegram_id,},
                {"$set": {"name": name}}
            )
            return True
        except:
            return False
        
    def add_point_to_total_user(self, telegram_id: int) -> None:
        """
        Добавляет единицу к общей статистике регистраций

        >>> INPUT: add_name_to_user(telegram_id: int)
        >>> OUTPUT: True - выполнилось, False - не смогло
        """
        try:
            self.users.update_one(
                {"telegram_id": telegram_id,},
                {"$inc": {"count_reg": 1}}
            )
            return True
        except:
            return False
    
    def add_point_to_accepted_user(self, telegram_id: int) -> None:
        """
        Добавляет единицу к статистике успешной регистрации

        >>> INPUT: add_name_to_user(telegram_id: int)
        >>> OUTPUT: True - выполнилось, False - не смогло
        """
        try:
            self.users.update_one(
                {"telegram_id": telegram_id,},
                {"$inc": {"count_visits": 1}}
            )
            return True
        except:
            return False
        
    def add_in_admins_data(self, telegram_id: int) -> bool:
        """
        Добавление нового администратора

        >>> add_in_admins_data(telegram_id: int)
        >>> OUTPUT: False - уже есть, True - записал
        """
        if self.admins.count_documents({"telegram_id": telegram_id}):
            return False
        else:
            self.admins.insert_one(
                {"telegram_id": telegram_id, "added": datetime.now()})
            return True
    
    def grid_admins_data(self) -> list:
        """
        Запрашивает список всех telegram id админов

        >>> INPUT: grid_admins_data()
        >>> OUTPUT: list
        """
        if not self.admins.count_documents({}):
            for telegram_id in Checker.owners.value:
                self.admins.insert_one(
                    {"telegram_id": telegram_id, "added": datetime.now()})
        
        return [telegram_id.get('telegram_id') for telegram_id in self.admins.find({}, {'telegram_id'})]
    
    def register_day(self, telegram_id: int, date: str, couple: str) -> None:
        """
        Запись регистрации в БД
        """
        day = self.days.find_one({date: {"$exists": True}})
        if day:
            if couple in day[date]:
                self.days.update_one({date: {couple: {"$exists": True}}}, {"$addToSet": {f"{date}.{couple}": telegram_id}})
            else:
                self.days.update_one({date: {"$exists": True}}, {"$set": {f"{date}.{couple}": [telegram_id]}})
        else:
            self.days.insert_one({date: {couple: [telegram_id]}})

    def get_records_between_dates(self):
        """
        Вывод информации о записях от start_date до end_date
        """
        today = datetime.now()
        start_date = today - timedelta(days=today.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        text = ""
        for day in range(7):
            date = str(start_date + timedelta(days=day))
            text += f"{date.split()[0]}\n"
            if data := self.days.find_one({date: {"$exists": True}}):
                for key, telegram_id in data[date].items():
                    text += f"{key} - записано {len(telegram_id)} человек. {telegram_id=}\n"
            else:
                text += "Записей нету на этот день.\n"
        
        return text





if __name__ == "__main__":
    from datetime import datetime, timedelta
    x = MongoDataBase()
    #print(x.grid_admins_data())
    #print(x.add_in_admins_data(1))
    #print(x.add_name_to_user(1, "John"))
    #print(x.get_records_between_dates())

