from aiogram.loggers import event
from aiogram.methods import EditMessageText
from sqlalchemy import Update

from config import bot, logger, ADMIN_IDS
from aiogram import BaseMiddleware, types
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from aiogram.exceptions import TelegramBadRequest
from app.database.models import UserStatus

import app.database.requests as rq
import data.user_messages as umsg
import app.keyboards.user_keyboards as ukb
import app.keyboards.admin_keyboards as akb

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
            message_id = event.message.message_id
            # записываем номер сообщения в базу данных
            await rq.update_user_last_message_id(user_tg_id=user_id, message_id=message_id)
            # лог
            logger.info(f'MW: {user.telegram_id} ({user.ident_name}) call "{event.data}" from "{event.message.text}" ({message_id})')
        # если пользователь отправил сообщение
        elif isinstance(event, Message):
            message_id = event.message_id
            # записываем номер сообщения в базу данных
            await rq.update_user_last_message_id(user_tg_id=user_id, message_id=message_id)
            # лог
            logger.info(f'MW: {user.telegram_id} ({user.ident_name}) send "{event.text}" ({message_id})')
            # в этом случае удаляем то, что отправил пользователь
            try:
                await bot.delete_message(chat_id=user_id, message_id=message_id)
            except TelegramBadRequest as e:
                logger.error(f'Ошибка удаления МИДЛВАРЬ: {message_id} - {e}')

        result = await handler(event, data)

        # находим последнее сообщение
        after_last_message_num = await rq.get_user_last_message_id(event.from_user.id)
        # удаляем последнее сообщение если его номер не равен предыдущегому (было новое, а не отредактированное)
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
                if update.callback_query.data == umsg.USER_MSG_REQUEST_WHEN_BLOCKED:
                    await update.callback_query.answer()
                    await update.callback_query.message.edit_text(umsg.USER_MSG_REQUEST_SENDED)
                    # если он в ожидании - то есть его не удалили совсем
                    if user.status == UserStatus.WAITING:
                        message_text = f"Пользователь {user.telegram_id} - {user.ident_name} просит его разблокировать"
                        for admin in ADMIN_IDS:
                            await bot.send_message(admin, message_text,
                                                   reply_markup=await akb.admin_block_menu(user_tg_id=user_id))

        # теперь проверяем активный ли пользователь, пропускаем дальше
        if is_returning:
            result = await handler(update, data)
            return result
        else:
            user = await rq.get_users_by_filters(user_tg_id=update_message.chat.id)
            if user.status == UserStatus.BLOCKED:
                await bot.send_message(update_message.chat.id, umsg.USER_MSG_WHEN_BLOCKED,
                                       reply_markup=await ukb.inline_block_menu())
                await rq.update_user_status(update_message.chat.id, UserStatus.WAITING)
            elif user.status == UserStatus.WAITING:
                await bot.send_message(update_message.chat.id, umsg.USER_MSG_WHEN_WAITING)
            elif user.status == UserStatus.DELETED:
                await bot.send_message(update_message.chat.id, umsg.USER_MSG_WHEN_DELETED)
