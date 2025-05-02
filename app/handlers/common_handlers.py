from aiogram import F, Router
from aiogram.filters.command import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
import app.handlers.callback_messages as callmsg
import app.keyboards.user_keyboards as ukb
import data.common_messages as cmsg
import app.database.requests as rq
from config import bot, logger
from app.utils.admin_utils import message_answer


common_router = Router()

# стартовая кнопка с зависимостью от админ или юзер
@common_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext):
    # чистим стейт
    await state.clear()
    # проверяем пользователя и регистрируем при необходимости
    # await rq.set_user(message)
    message_text = cmsg.START_MESSAGE.format(message.from_user.first_name)
    reply_kb = await ukb.common_main_kb(user_tg_id= message.from_user.id)
    await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
    # try:
    #     await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    #     logger.info(f'{message.from_user.id} нажал СТАРТ. common handlers удалил start message')
    # except TelegramBadRequest as e:
    #     logger.error(f'ошибка удаления common handlers start message {e}')


# команда хелп
@common_router.message(Command('help'))
async def get_help(message: Message):
    logger.info(f'{message.from_user.id}-отправил сообщение: {message.text}')
    message_text = cmsg.HELP_MESSAGE
    await message_answer(source=message, message_text=message_text)


# действия при нажатии инлайн кнопки главное меню с удалением или редактированием сообщения
@common_router.callback_query(F.data == callmsg.CALL_PRESS_MAIN_MENU)
async def main_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    message_text = cmsg.PRESS_ANY_BUTTON
    reply_kb = await ukb.common_main_kb(user_tg_id= call.from_user.id)
    await message_answer(source=call, message_text=message_text, reply_markup=reply_kb)
    await call.answer()


# произвольное сообщение
@common_router.message(F.text)
async def to_main_menu(message: Message):
    message_text = cmsg.I_DONT_UNDERSTAND
    reply_kb = await ukb.common_main_kb(user_tg_id= message.from_user.id)
    await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)


# произвольный call
@common_router.callback_query(F.data)
async def any_call(call: CallbackQuery):
    logger.info(f'{call.from_user.username} ({call.from_user.first_name})'
                f' - непонятный call *{call.data}*')
    await call.answer(f'{cmsg.I_DONT_UNDERSTAND}, call: {call.data}', show_alert=True)

# произвольный call
@common_router.message(F.photo)
async def to_main_menu(message: Message):
    await message.answer(message.photo[-1].file_id, reply_markup=await ukb.common_main_kb(user_tg_id= message.from_user.id))
    try:
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
    except TelegramBadRequest as e:
        logger.error(f'{message.from_user.username} ({message.from_user.first_name})'
                     f' - ошибка при удалении сообщения id по *{message.text}*: {e}')

@common_router.message(F.video)
async def to_main_menu(message: Message):
    await message.answer(message.video.file_id,
                         reply_markup=await ukb.common_main_kb(user_tg_id=message.from_user.id))
    try:
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
    except TelegramBadRequest as e:
        logger.error(f'{message.from_user.username} ({message.from_user.first_name})'
                     f' - ошибка при удалении сообщения id по *{message.text}*: {e}')




