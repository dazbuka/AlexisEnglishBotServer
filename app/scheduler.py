import asyncio, re
from aiogram import Bot
from datetime import datetime
import  app.database.requests as rq
from config import logger
from config import DEVELOPER_ID
from app.database.models import Task, User
from aiogram.exceptions import TelegramBadRequest
from app.keyboards.keyboard_builder import keyboard_builder
from app.keyboards.menu_buttons import *

async def send_reminders(bot: Bot):
    user_list : list[User]= await rq.get_users_by_filters(status='ACTIVE')
    now_time = datetime.now().time().strftime("%H:%M")
    now_date = datetime.now().date().strftime("%d.%m.%Y")
    # перебираем всех пользователей
    for user in user_list:
        interval_list = user.intervals.split(',')
        if now_time in interval_list:
            tasks : list[Task]= await rq.get_tasks_by_filters(user_id=user.id,
                                                              sent=False,
                                                              media_task_only=True,
                                                              daily_and_missed=True)
            if tasks:
                reply_kb = await keyboard_builder(menu_pack=[[button_quick_menu, button_main_menu]])
                if len(tasks) < 11:
                    tasks_text = '\n- '.join({task.media.collocation for task in tasks})
                    message_text = f'{MESS_YOU_HAVE_TASKS.format(len(tasks))}\n\nCollocations: {tasks_text}'
                else:
                    message_text = f'{MESS_YOU_HAVE_TASKS.format(len(tasks))}'
                reminder_mess = await bot.send_message(chat_id=user.telegram_id,
                                                       text=message_text,
                                                       reply_markup=reply_kb)
                try:
                    await bot.delete_message(chat_id=user.telegram_id, message_id=user.last_message_id)
                except TelegramBadRequest as e:
                    logger.warning(f'ошибка удаления {user.last_message_id} sheduler {e}')
                await rq.update_user_last_message_id(user_tg_id=user.telegram_id, message_id=reminder_mess.message_id)

    # сообщение мне, временно
    if now_time[3:5] == '00':
        reply_kb = await keyboard_builder(menu_pack=[[button_main_menu]])
        await bot.send_message(DEVELOPER_ID, f'Time: {now_time} - {len(user_list)} active users', reply_markup=reply_kb)

    if now_time[0:5] == '14:30' and now_date == '09.05.2025' :
        for user in user_list:
            reply_kb = await keyboard_builder(menu_pack=[[button_main_menu]])
            await bot.send_message(user.telegram_id, f"AlexisEnglishBot has been updated. "
                                                          f"It is recommended to clear the history and "
                                                          f"start by tapping the main menu or start button.",
                                                          reply_markup=reply_kb)

async def check_reminders(bot: Bot):
    while True:
        await send_reminders(bot)
        await asyncio.sleep(60)  # Запускаем проверку раз в минуту