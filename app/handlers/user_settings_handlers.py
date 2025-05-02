from aiogram.fsm.state import State, StatesGroup
from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from config import logger
import app.utils.admin_utils as aut
import app.database.requests as rq
import app.keyboards.user_keyboards as ukb
import app.handlers.callback_messages as callmsg
import data.user_messages as umsg
import data.common_messages as cmsg


user_settings_router = Router()

class AddInterval(StatesGroup):
    intervals = State()


# хендлер перехода в меню settings - пункт главного меню
@user_settings_router.callback_query(F.data == cmsg.COMMON_BUTTON_SETTINGS)
async def show_settings_menu(call : CallbackQuery, state: FSMContext):
    # сообщение логгеру
    logger.info(f'{call.from_user.username} ({call.from_user.first_name})'
                f' - вход в меню settings по *{call.data}*')
    # очищаем стейт на всякий случай
    await state.clear()
    # клавиатура для дальнейшего вывода
    reply_kb = await ukb.inline_settings_menu()
    await call.message.edit_text(umsg.USER_BUTTON_SETTINGS, reply_markup=reply_kb)
    await call.answer()


# хендлер перехода в меню settings - пункт главного меню
@user_settings_router.callback_query(F.data == umsg.USER_REVISION_BUTTON_REMINDER_TIME)
async def set_reminder_interval(call: CallbackQuery, state: FSMContext):
    # сообщение логгеру
    logger.info(f'{call.from_user.username} ({call.from_user.first_name})'
                f' - вход в меню set remindre interval по *{call.data}*')
    user = await rq.get_users_by_filters(user_tg_id=call.from_user.id)
    all_intervals = await aut.get_reminder_all_day_intervals()
    set_int = user.intervals
    if set_int:
        interval_list = set_int.replace(' ', '').split(',')
        setted_intervals = await aut.set_check_in_list(checked_list=all_intervals, checked_items=interval_list)
    else:
        setted_intervals = all_intervals
    # клавиатура для дальнейшего вывода
    reply_kb = await ukb.inline_settings_intervals_buttons_kb(setted_intervals)
    # reply_kb = await ukb.inline_settings_intervals_buttons_kb(all_intervals)
    await call.message.edit_text(umsg.USER_INVITE_INTERVALS, reply_markup=reply_kb)
    await state.set_state(AddInterval.intervals)
    await state.update_data(intervals=setted_intervals)
    await call.answer()


# хендлер перехода в меню settings - пункт главного меню
@user_settings_router.callback_query(F.data.startswith(callmsg.CALL_SETTINGS_INTERVAL))
async def set_interval(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбэка выбранный интервал
    interval_call = call.data.replace(callmsg.CALL_SETTINGS_INTERVAL, '')
    intervals = (await state.get_data()).get('intervals')
    if interval_call == callmsg.CALL_USER_END_CHOOSING:
        new_intervals = []
        for i in range(len(intervals)):
            if intervals[i][0] == '🟣':
                new_intervals.append(intervals[i][1:-1])
        intervals_for_db = ','.join(map(str, new_intervals))
        await rq.update_user_intervals(user_tg_id=int(call.from_user.id), intervals=intervals_for_db)
        #
        if intervals_for_db:
            message_text = f'Сохранено время уведомлений:\n{intervals_for_db}\nВыберите пункт меню:'
        else:
            message_text = f'Все уведомления удалены!\n{intervals_for_db}\nВыберите пункт меню:'
        await call.message.edit_text(message_text, reply_markup=await ukb.inline_settings_menu())
        await call.answer()
    else:
        intervals = await aut.set_check_in_list(checked_list=intervals, checked_item=interval_call)
        reply_kb = await ukb.inline_settings_intervals_buttons_kb(intervals)
        await call.message.edit_text(f'Добавьте еще и нажмите подтвердить', reply_markup=reply_kb)
        await state.update_data(intervals=intervals)
        await call.answer()
        await state.set_state(AddInterval.intervals)




