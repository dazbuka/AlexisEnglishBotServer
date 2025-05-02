from aiogram import F, Router
from aiogram.types import CallbackQuery
from config import logger
from datetime import datetime, timedelta
from aiogram.exceptions import TelegramBadRequest
import app.database.requests as rq

import data.user_messages as umsg

user_router = Router()


# инлайн кнопка просмотра определения на английском
@user_router.callback_query(F.data.startswith(umsg.USER_BUTTON_DEFINITION))
async def show_definition(call: CallbackQuery):
    # вытаскиваем из колбека номер слова и берем его из базы данных
    word_id=int(call.data.replace(umsg.USER_BUTTON_DEFINITION, ''))
    words = await rq.get_words_by_filters(word_id=word_id)
    word = words[0] if words else None
    try:
        await call.answer(f'{word.word} - {word.definition}', show_alert=True)
    except TelegramBadRequest as e:
        logger.error(f'{call.from_user.username} ({call.from_user.first_name})'
                     f' - ошибка definition для {word.word} *{call.data}*: {e}')
        await call.answer(f"Can't show definition, because it is too long", show_alert=True)


# инлайн кнопка просмотра перевода
@user_router.callback_query(F.data.startswith(umsg.USER_BUTTON_TRANSLATION))
async def show_translation(call: CallbackQuery):
    # вытаскиваем из колбека номер слова и берем его из базы данных
    word_id=int(call.data.replace(umsg.USER_BUTTON_TRANSLATION, ''))
    words = await rq.get_words_by_filters(word_id=word_id)
    word = words[0] if words else None
    try:
        await call.answer(f'{word.word} - {word.translation}', show_alert=True)
    except TelegramBadRequest as e:
        logger.error(f'{call.from_user.username} ({call.from_user.first_name})'
                     f' - ошибка translation для {word.word} *{call.data}*: {e}')
        await call.answer(f"Can't show translation, because it is too long", show_alert=True)


# инлайн кнопка отправки медиа на повторение сегодня
@user_router.callback_query(F.data.startswith(umsg.USER_BUTTON_REPEAT_TODAY))
async def repeat_today(call: CallbackQuery):
    # вытаскиваем из колбека номер коллокации и пользователя
    media_id=int(call.data.replace(umsg.USER_BUTTON_REPEAT_TODAY, ''))
    user = await rq.get_users_by_filters(user_tg_id=call.from_user.id)
    # добавляем задание на сегодня
    await rq.set_task(user_id=user.id, media_id=media_id, task_time=datetime.now(), author_id=user.id)
    await call.answer('Task added')


# инлайн кнопка отправки медиа на повторение завтра
@user_router.callback_query(F.data.startswith(umsg.USER_BUTTON_REPEAT_TOMORROW))
async def repeat_tomorrow(call: CallbackQuery):
    # вытаскиваем из колбека номер коллокации и пользователя
    media_id=int(call.data.replace(umsg.USER_BUTTON_REPEAT_TOMORROW, ''))
    user = await rq.get_users_by_filters(user_tg_id=call.from_user.id)
    # добавляем задание на завтра
    await rq.set_task(user_id=user.id, media_id=media_id, task_time=datetime.now()+timedelta(days=1), author_id=user.id)
    await call.answer('Task added')
