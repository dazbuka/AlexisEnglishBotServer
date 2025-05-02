import asyncio
import logging
from aiogram.types import BotCommand, BotCommandScopeDefault

from aiogram import types

from config import bot, dp, logger, DEVELOPER_ID
from app.database.models import async_main
from app.scheduler import check_reminders

from app.handlers.common_handlers import common_router
from app.handlers.admin_handlers import admin_router
from app.handlers.admin_adding_word_handlers import admin_adding_word_router
from app.handlers.admin_adding_media_handlers import admin_adding_media_router
from app.handlers.admin_adding_test_handlers import admin_adding_test_router
from app.handlers.admin_adding_task_handlers import admin_adding_task_router
from app.handlers.admin_adding_homework_handlers import admin_adding_homework_router
from app.handlers.user_handlers import user_router
from app.handlers.user_studing_handlers import user_studying_router
from app.handlers.user_revision_handlers import user_revision_router
from app.handlers.user_homework_handlers import user_homework_router
from app.handlers.user_settings_handlers import user_settings_router


from app.middlewares import BlockingUserMiddleware, DeletingAndLoggingMessagesMiddleware

# Функция, которая настроит командное меню (дефолтное для всех пользователей)
async def set_commands():
    commands = [BotCommand(command='start', description='Старт')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())

# Функция, которая выполнится, когда бот запустится
async def start_bot():
    await set_commands()
    try:
        await bot.send_message(DEVELOPER_ID, f'AlexisEnglishBot started')
        print("bot started")
    except:
        pass
    logger.info("Бот успешно запущен.")


# Функция, которая выполнится, когда бот завершит свою работу
async def stop_bot():
    try:
        await bot.send_message(DEVELOPER_ID, f'AlexisEnglishBot stopped')
    except:
        pass
    logger.info("Бот остановлен!")


async def main():
    # создание базы данных, таблиц, если их нет
    await async_main()
    # удаляем вебхуки, сообщения, накопившиеся за время, пока бот не работал
    await bot.delete_webhook(drop_pending_updates=True)
    # подключаем роутеры и мидлварь
    dp.update.middleware(BlockingUserMiddleware())
    dp.callback_query.middleware(DeletingAndLoggingMessagesMiddleware())
    dp.message.middleware(DeletingAndLoggingMessagesMiddleware())


    dp.include_routers(user_studying_router,
                       user_revision_router,
                       user_settings_router,
                       user_homework_router,
                       user_router,
                       admin_adding_word_router,
                       admin_adding_media_router,
                       admin_adding_test_router,
                       admin_adding_task_router,
                       admin_adding_homework_router,
                       admin_router,
                       common_router)
    # подключаем проверку напоминалок в промежутках времени

    asyncio.create_task(check_reminders(bot))
    # фукнции, выполняющиеся при запуске и остановке бота
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    # поехали
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')



