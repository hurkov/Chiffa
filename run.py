import asyncio, logging
from aiogram import Bot, Dispatcher
from datetime import datetime
import app.db as db 

from app.commands import rtc
from app.chats_status import rt

bot = Bot('TOKEN') 
dp = Dispatcher()

async def onstartup():
    await db.db_start()
    print('Db successfuly started')

async def main():
    print(f'Programm started at {datetime.now()}')
    dp.include_router(rt)
    dp.include_router(rtc)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(onstartup())
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
