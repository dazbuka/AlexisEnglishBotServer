from config import bot
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import app.keyboards.admin_keyboards as akb
import app.keyboards.user_keyboards as ukb
import app.database.requests as rq
from app.utils.admin_utils import message_answer
import data.admin_messages as amsg
from app.database.models import UserStatus

admin_router = Router()


# переход в админское меню call
@admin_router.callback_query(F.data == amsg.ADMIN_BUTTON_MAIN_ADMIN_MENU)
async def admin_menu_button(call: CallbackQuery, state: FSMContext):
    await state.clear()
    message_text = 'Welcome to main admin menu'
    reply_kb = await akb.main_admin_menu_kb()
    await message_answer(source=call, message_text=message_text, reply_markup=reply_kb)
    await call.answer()


# переход в админское меню call
@admin_router.callback_query(F.data == amsg.ADMIN_BUTTON_ADDING_MENU)
async def admin_adding_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    message_text = amsg.ADMIN_ADDING_MENU_WELCOME
    reply_kb = await akb.admin_adding_menu_kb()
    await message_answer(source=call, message_text=message_text, reply_markup=reply_kb)
    await call.answer()


# разблокировка или удаление пользователя
@admin_router.callback_query(F.data.startswith(amsg.ADMIN_BUTTON_UNBLOCK_USER))
async def unblock_user(call: CallbackQuery, state: FSMContext):
    await state.clear()
    # вытаскиваем из колбека номер пользователя
    user_tg_id = int(call.data.replace(amsg.ADMIN_BUTTON_UNBLOCK_USER, ''))
    # меняем статус
    await rq.update_user_status(user_tg_id, UserStatus.ACTIVE)
    # отвечаем админу
    await message_answer(source=call, message_text='Пользователь разблокирован',
                         reply_markup=await ukb.common_main_kb(call.from_user.id))
    # отвечаем разблокированному пользователю
    await bot.send_message(user_tg_id, "--Unblocked--. \nHello!", reply_markup=await ukb.common_main_kb(user_tg_id))
    await call.answer()


# удаление пользователя
@admin_router.callback_query(F.data.startswith(amsg.ADMIN_BUTTON_DELETE_USER))
async def delete_user(call: CallbackQuery, state: FSMContext):
    await state.clear()
    # вытаскиваем из колбека номер пользователя
    user_tg_id = int(call.data.replace(amsg.ADMIN_BUTTON_DELETE_USER, ''))
    # меняем статус
    await rq.update_user_status(user_tg_id, UserStatus.DELETED)
    # отвечаем админу
    await message_answer(source=call, message_text='Пользователь удален',
                         reply_markup=await ukb.common_main_kb(call.from_user.id))
    # отвечаем разблокированному пользователю
    await bot.send_message(user_tg_id, "--Deleted--. \nBy!")
    await call.answer()