from time import sleep

from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton
)
from config import bot, logger, ADMIN_IDS
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from aiogram.exceptions import TelegramBadRequest
from app.database.models import UserStatus
import app.database.requests as rq
from app.common_settings import *


class DeletingAndLoggingMessagesMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        # вытаскиваем номер пользователя
        user_id = event.from_user.id
        # берем данные пользователя
        user = await rq.get_users_by_filters(user_tg_id=user_id)
        # находим последнее сообщение
        before_last_message_num = await rq.get_user_last_message_id(user_id)
        # вытаскиваем номер сообщения в зависимости от типа объекта
        # если это нажатие на кнопку (колбэк)
        if isinstance(event, CallbackQuery):
            # print(f'----------------------------------{event.data}--------------------------------------')
            message_id = event.message.message_id
            # записываем номер сообщения в базу данных
            await rq.update_user_last_message_id(user_tg_id=user_id, message_id=message_id)
            # убираем переносы из текста для логгера
            if event.message.text:
                text = event.message.text.replace('\n',' ')
            else:
                text = "None"
            # лог
            # logger.info(f'MW: {user.telegram_id} ({user.ident_name}) call "{event.data}" '
            #             f'from "{text}" ({message_id})')
        # если пользователь отправил сообщение
        elif isinstance(event, Message):
            # print(f'----------------------------------{event.text}--------------------------------------')
            # print(f'----------------------------------{event.caption}--------------------------------------')
            message_id = event.message_id
            # записываем номер сообщения в базу данных
            await rq.update_user_last_message_id(user_tg_id=user_id, message_id=message_id)
            # убираем переносы из текста для логгера
            if event.text:
                text = event.text.replace('\n', ' ')
            else:
                text = "None"
            # лог
            # logger.info(f'MW: {user.telegram_id} ({user.ident_name}) send "{text}" ({message_id})')
            # .replace('\n','')
            # в этом случае удаляем то, что отправил пользователь
            try:
                await bot.delete_message(chat_id=user_id, message_id=message_id)
            except TelegramBadRequest as e:
                logger.error(f'Ошибка удаления МИДЛВАРЬ: {message_id} - {e}')

        result = await handler(event, data)

        # находим последнее сообщение
        after_last_message_num = await rq.get_user_last_message_id(event.from_user.id)
        # удаляем последнее сообщение если его номер не равен предыдущегому (было новое, а не отредактированное)
        sleep(0.5)
        if before_last_message_num != after_last_message_num:
            try:
                await bot.delete_message(chat_id=user_id, message_id=before_last_message_num)
            except TelegramBadRequest as e:
                logger.error(f'ошибка удаления middleware {before_last_message_num} - {e}')

        return result


class BlockingUserMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       update: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        # переменная для блокировки пользователя
        is_returning = False
        # вытаскиваем объект message в зависимости от типа телеграмобжекта, проверяем только 2 типа
        update_message = None
        if update.message:
            update_message = update.message
        elif update.callback_query:
            update_message = update.callback_query.message

        # если объект сообщение или колбэк есть то работаем:
        if update_message:
            # регистрируем пользователя, если не существует
            await rq.set_user(update_message)
            # вытаскиваем номер телеграм пользователя
            user_id = update_message.chat.id
            # берем данные пользователя
            user = await rq.get_users_by_filters(user_tg_id=user_id)
            # проверяем статус, пропускаем, меняем переменную для возврата ответа
            if user:
                if user.status == 'ACTIVE':
                    is_returning = True

            # дополнительно проверям, не шлет ли заблокированный пользователь запрос на разблокировку
            if update.callback_query:
                if update.callback_query.data == USER_MSG_REQUEST_WHEN_BLOCKED:
                    await update.callback_query.answer()
                    await update.callback_query.message.edit_text(USER_MSG_REQUEST_SENDED)
                    # если он в ожидании - то есть его не удалили совсем
                    if user.status == UserStatus.WAITING:
                        message_text = f"Пользователь {user.telegram_id} - {user.ident_name} просит его разблокировать"
                        for admin in ADMIN_IDS:
                            user_tg_id = update.from_user.id
                            inline_keyboard = [
                                [
                                    InlineKeyboardButton(text=ADMIN_BUTTON_UNBLOCK_USER,
                                                         callback_data=f'{ADMIN_BUTTON_UNBLOCK_USER}{user_tg_id}')
                                ],
                                [
                                    InlineKeyboardButton(text=ADMIN_BUTTON_DELETE_USER,
                                                         callback_data=f'{ADMIN_BUTTON_DELETE_USER}{user_tg_id}')
                                ]
                            ]
                            await bot.send_message(admin, message_text,
                                                   reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard))

        # теперь проверяем активный ли пользователь, пропускаем дальше
        if is_returning:
            result = await handler(update, data)
            return result
        else:
            user = await rq.get_users_by_filters(user_tg_id=update_message.chat.id)
            if user.status == UserStatus.BLOCKED:
                await bot.send_message(update_message.chat.id,
                    USER_MSG_WHEN_BLOCKED,
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=USER_MSG_REQUEST_WHEN_BLOCKED,
                                              callback_data=USER_MSG_REQUEST_WHEN_BLOCKED)]
                    ]))
                await rq.update_user_status(update_message.chat.id, UserStatus.WAITING)
            elif user.status == UserStatus.WAITING:
                await bot.send_message(update_message.chat.id, USER_MSG_WHEN_WAITING)
            elif user.status == UserStatus.DELETED:
                await bot.send_message(update_message.chat.id, USER_MSG_WHEN_DELETED)
            return
