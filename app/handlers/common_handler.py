from aiogram import F, Router
from aiogram.filters.command import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from config import bot, logger, DEVELOPER_ID
from app.database.requests import (delete_media_from_db, get_users_by_filters, update_user_status,
                                   update_user_intervals_temp_alembic, get_medias_by_filters)
from app.admin_utils import message_answer
from app.database.models import UserStatus
from app.keyboards.keyboard_builder import keyboard_builder
from app.keyboards.menu_buttons import *
from app.database.models import User, Media

common_router = Router()

@common_router.callback_query(F.data == CALL_DELETE_TEST_MEDIA)
async def update(call: CallbackQuery, state: FSMContext):
    await state.clear()
    # вытаскиваем из колбека номер пользователя
    medias : list[Media]= await get_medias_by_filters(test_only=True)
    for media in medias:
        await delete_media_from_db(media.id)
    await call.answer('Tests deleted')

@common_router.callback_query(F.data == CALL_UPDATE_USER_INTERVALS)
async def update(call: CallbackQuery, state: FSMContext):
    await state.clear()
    # вытаскиваем из колбека номер пользователя
    users : list[User]= await get_users_by_filters()
    for user in users:
        curr_int_list = user.intervals.split(',')
        curr_int_list_new = [x[:5] for x in curr_int_list]
        new_str = ','.join(curr_int_list_new)
        await update_user_intervals_temp_alembic(user_id=user.id, intervals=new_str)
    # меняем статус
    await call.answer('Intervals updated')


# разблокировка или удаление пользователя
@common_router.callback_query(F.data.startswith(ADMIN_BUTTON_UNBLOCK_USER))
async def unblock_user(call: CallbackQuery, state: FSMContext):
    await state.clear()
    # вытаскиваем из колбека номер пользователя
    user_tg_id = int(call.data.replace(ADMIN_BUTTON_UNBLOCK_USER, ''))
    # меняем статус
    await update_user_status(user_tg_id, UserStatus.ACTIVE)

    reply_kb = await keyboard_builder(menu_pack=[[button_main_menu_back]])

    # отвечаем админу
    await message_answer(source=call, message_text='Пользователь разблокирован',
                         reply_markup=reply_kb)
    # отвечаем разблокированному пользователю

    await bot.send_message(user_tg_id, "--Unblocked--. \nHello!", reply_markup=reply_kb)
    await call.answer()


# удаление пользователя
@common_router.callback_query(F.data.startswith(ADMIN_BUTTON_DELETE_USER))
async def delete_user(call: CallbackQuery, state: FSMContext):
    await state.clear()
    # вытаскиваем из колбека номер пользователя
    user_tg_id = int(call.data.replace(ADMIN_BUTTON_DELETE_USER, ''))
    # меняем статус
    await update_user_status(user_tg_id, UserStatus.DELETED)
    # отвечаем админу
    reply_kb = await keyboard_builder(menu_pack=[[button_main_menu_back]])
    await message_answer(source=call, message_text='Пользователь удален',
                         reply_markup=reply_kb)
    # отвечаем разблокированному пользователю
    await bot.send_message(user_tg_id, "--Deleted--. \nBy!")
    await call.answer()


# команда хелп
@common_router.message(Command('help'))
async def get_help(message: Message):
    await bot.send_message(DEVELOPER_ID, f'{message.from_user.username} ({message.from_user.first_name}) '
                                         f'отправил {message.text}')
    message_text = MESS_HELP
    await message_answer(source=message, message_text=message_text)



# произвольный call
@common_router.callback_query(F.data)
async def any_call(call: CallbackQuery):
    logger.info(f'{call.from_user.username} ({call.from_user.first_name})'
                f' - непонятный call *{call.data}*')
    await bot.send_message(DEVELOPER_ID, f'{call.from_user.username} ({call.from_user.first_name})'
                f' - непонятный call *{call.data}*')
    # await call.answer(f'{MESS_DONT_UNDERSTAND}, call: {call.data}', show_alert=True)
    await call.answer()


# произвольное сообщение
@common_router.message(F.text)
async def to_main_menu(message: Message):
    message_text = MESS_DONT_UNDERSTAND
    reply_kb = await keyboard_builder(menu_pack=[[button_main_menu_back]])
    await bot.send_message(DEVELOPER_ID, f'{message.from_user.username} ({message.from_user.first_name}) '
                                         f'отправил текст, который не обработан ботом текст {message.text}')
    await message.answer(message_text, reply_markup=reply_kb)


# произвольный call
@common_router.message(F.photo)
async def to_main_menu(message: Message):
    reply_kb = await keyboard_builder(menu_pack=[[button_main_menu_back]])
    await bot.send_message(DEVELOPER_ID, f'{message.from_user.username} ({message.from_user.first_name}) '
                                         f'отправил фото {message.photo[-1].file_id}')
    await message.answer(message.photo[-1].file_id, reply_markup=reply_kb)


@common_router.message(F.video)
async def to_main_menu(message: Message):
    reply_kb = await keyboard_builder(menu_pack=[[button_main_menu_back]])
    await bot.send_message(DEVELOPER_ID, f'{message.from_user.username} ({message.from_user.first_name}) '
                                         f'отправил видео {message.video.file_id}')
    await message.answer(message.video.file_id, reply_markup=reply_kb)




