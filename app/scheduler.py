import asyncio
from aiogram import Bot
from datetime import datetime
import  app.database.requests as rq
from config import logger
from config import (DEVELOPER_ID, REMINDER_INTERVAL, REMINDER_SLEEP_INTERVAL, SENDING_SLEEP_INTERVAL)
from app.utils.admin_utils import count_user_tasks_by_tg_id, check_now_time_in_reminder_intervals
import data.common_messages as cmsg
import app.keyboards.user_keyboards as ukb
from aiogram.exceptions import TelegramBadRequest


async def send_reminders(bot: Bot) -> int:
    logger.info('бот работает, проверка связи раз в час')
    user_list = await rq.get_users_by_filters()
    text = 'Bot is working:\n'

    sleeping_while_sending = 0
    # перебираем всех пользователей
    for user in user_list:
        if user.status == 'ACTIVE':
            # подсчитываем задания
            tasks_counter = await count_user_tasks_by_tg_id(user_tg_id=user.telegram_id)
            daily_count = tasks_counter['daily']
            missed_count = tasks_counter['missed']
            # дописываем текст сообщения админу
            text = text + f'{user.username} has {daily_count} daily, {missed_count} missed\n'
            if daily_count != 0:
                if await check_now_time_in_reminder_intervals(user.intervals):
                    last_msg = await rq.get_user_last_message_id(user.telegram_id)
                    r_mess = await bot.send_message(user.telegram_id,
                                                    cmsg.YOU_HAVE_TASKS.format(daily_count+missed_count),
                                                    reply_markup=await ukb.common_main_kb(user_tg_id=user.telegram_id))
                    try:
                        await bot.delete_message(chat_id=user.telegram_id, message_id=last_msg)
                        logger.info(f'sheduler удалил {last_msg}')
                    except TelegramBadRequest as e:
                        logger.error(f'ошибка удаления {last_msg} sheduler {e}')
                    logger.info(f'отправил напоминание {user.username} ({user.first_name}, {user.telegram_id}), '
                                f'что у него есть {daily_count+missed_count} заданий')
                    await rq.update_user_last_message_id(user_tg_id=user.telegram_id, message_id=r_mess.message_id)
                sleeping_while_sending += SENDING_SLEEP_INTERVAL
                await asyncio.sleep(SENDING_SLEEP_INTERVAL)
    # сообщение мне, временно
    await bot.send_message(DEVELOPER_ID, text)
    return sleeping_while_sending


async def check_reminders(bot: Bot):
    while True:
        # берем из настроек начало и конец работы ремайндера, сравниваем с текущим временем и запускаем функцию
        day_start = datetime.strptime(REMINDER_INTERVAL.split(' - ')[0], "%H:%M").time()
        day_end = datetime.strptime(REMINDER_INTERVAL.split(' - ')[1], "%H:%M").time()
        now = datetime.now().time()
        sleeping_while_sending = 0
        if day_start <= now <= day_end:
            sleeping_while_sending = await send_reminders(bot)
        await asyncio.sleep(REMINDER_SLEEP_INTERVAL - sleeping_while_sending)  # Запускаем раз в час