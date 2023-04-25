from aiogram import types

ADMIN_LIST: list = None

def set_admin_list(admin_list: list):
    global ADMIN_LIST
    ADMIN_LIST = admin_list

def is_admin(message: types.Message, id: int= None) -> bool:
    if id:
        return id in ADMIN_LIST
    else:
        return message.from_user.id in ADMIN_LIST

def admin_only(func):
    async def wrapper(self, message: types.Message):
        if is_admin(message):
            await func(self, message)
    return wrapper