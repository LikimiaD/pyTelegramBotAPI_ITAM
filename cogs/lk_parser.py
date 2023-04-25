import asyncio
import time
import ssl
import certifi
from functools import wraps

import aiohttp as aiohttp

def measure_time(func):
    import time
    async def wrap(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        print(f'Parsing complete for {time.perf_counter() - start} seconds')
        return result
    return wrap

class Schedule:
    days: list = ["day_1", "day_2", "day_3", "day_4", "day_5", "day_6"]

    def __init__(self, dct: dict):
        self.dct: dict = dct
        self.main: dict = {}
        self.__post_init__()

    def __post_init__(self):
        bell_1 = {}
        bell_2 = {}
        bell_3 = {}
        bell_4 = {}
        bell_5 = {}
        bell_6 = {}
        lst: dict = {"bell_1": bell_1, "bell_2": bell_2, "bell_3": bell_3, "bell_4": bell_4,
                     "bell_5": bell_5, "bell_6": bell_6}
        
        for str_lesson, lesson in lst.items():
            if self.dct.get(str_lesson):
                if self.dct[str_lesson].get("header"):
                    lesson_time = f'{self.dct[str_lesson]["header"]["start_lesson"]}-{self.dct[str_lesson]["header"]["end_lesson"]}'
                    lesson["time"] = lesson_time

                for day in self.days:
                    lesson[day] = []
                    if self.dct[str_lesson][day]["lessons"]:
                        lesson_name = self.dct[str_lesson][day]["lessons"][0]["subject_name"]
                        lesson[day] = lesson_name
                    else:
                        lesson[day] = None
        self.main = {bell['time']: list(bell.values())[1:] for bell in lst.values() if len(bell) > 0}
        
        
        


async def room_parse(task_name, session, room_id, start_date = None):
    print(f"Starting parse: {task_name}")
    PARAMS = {'room': room_id}
    url = 'https://lk.misis.ru/method/schedule.get'
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    response = await session.post(url, params=PARAMS, ssl_context=ssl_context)
    rooms_json = await response.json()

    return rooms_json

@measure_time
async def main():
    async with aiohttp.ClientSession() as session:
        from datetime import datetime, timedelta
        room_ids = [1298, 298]
        today = datetime.today()
        next_weekday = today.weekday() + 7

        tasks = []
        for room_id in room_ids:
            task = asyncio.gather(
                room_parse(f"|Current Week| room_id -> {room_id}", session, room_id),
                room_parse(f"|Next Week|    room_id -> {room_id}", session, room_id, today + timedelta(days=next_weekday))
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        return [[Schedule(sch[0]['schedule']), Schedule(sch[1]['schedule'])] for sch in results]


if __name__ == "__main__":
    room_1298, room_298 = asyncio.run(main())
    room_1298 = {"upper": room_1298[0].main,
                 "lower": room_1298[1].main}
    room_298 = {"upper": room_298[0].main,
                 "lower": room_298[1].main}
    for key, value in room_1298['upper'].items():
        print(key, value[2])
