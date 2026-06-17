import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import init_db_sync

# Инициализация БД
init_db_sync()

from handlers import router, set_bot

async def main():
    bot = Bot(token=BOT_TOKEN)
    set_bot(bot)
    
    dp = Dispatcher()
    dp.include_router(router)
    
    print("🚀 Бот кубиков запущен!")
    print(f"🆔 Админ: {ADMIN_IDS}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())