from aiogram.fsm.state import State, StatesGroup
from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from app.database.models import User
from app.keyboards.menu_buttons import *
from app.utils.admin_utils import state_text_builder
from app.database.requests import get_users_by_filters, update_user_intervals
from app.common_settings import *
from app.keyboards.keyboard_builder import keyboard_builder, update_button_with_check

config_router = Router()

menu_set_intervals = [[button_config_menu_back, button_main_menu_back]]

class IntervalsState(StatesGroup):
    intervals_state = State()


@config_router.callback_query(F.data == CALL_CONFIG_SENDING_TIME)
async def config_sending_time_start(call: CallbackQuery, state: FSMContext):
    # очистка стейта
    await state.clear()
    user : User = await get_users_by_filters(user_tg_id=call.from_user.id)
    set_of_intervals = {x[:5] for x in user.intervals.split(',')}
    print(set_of_intervals)

    await state.update_data(intervals_state=set_of_intervals)

    buttons_pack = [InlineKeyboardButton(text=f'{str(hour).zfill(2)}:00',
                                                  callback_data=f'{CALL_CONFIG_SENDING_TIME}{str(hour).zfill(2)}:00')
                                                  for hour in range(7,23)]
    buttons_pack = [update_button_with_check(button, CHECK_CONFIG_SENDING_TIME)
                    if button.text in set_of_intervals
                    else button
                    for button in buttons_pack]

    reply_kb = await keyboard_builder(menu_pack=menu_set_intervals,
                                      buttons_pack=buttons_pack,
                                      buttons_base_call=CALL_CONFIG_SENDING_TIME,
                                      buttons_cols=NUM_CONFIG_SENDING_TIME_COLS,
                                      buttons_rows=NUM_CONFIG_SENDING_TIME_ROWS,
                                      is_adding_confirm_button=True)

    state_text = await state_text_builder(state)
    message_text = state_text + '\n' + MESS_CONFIG_SENDING_TIME
    await call.message.edit_text(text=message_text, reply_markup=reply_kb)
    await state.set_state(IntervalsState.intervals_state)
    await call.answer()

# хендлер перехода в меню settings - пункт главного меню
@config_router.callback_query(F.data.startswith(CALL_CONFIG_SENDING_TIME), IntervalsState.intervals_state)
async def config_sending_time_loop(call: CallbackQuery, state: FSMContext):
    call_item = call.data.replace(CALL_CONFIG_SENDING_TIME, '')
    intervals_set = await state.get_value('intervals_state')
    if call_item == CALL_CONFIRM:
        intervals_str = ','.join(intervals_set)
        await update_user_intervals(user_tg_id=call.from_user.id, intervals=intervals_str)

        reply_kb = await keyboard_builder(menu_pack=menu_set_intervals)
        await call.message.edit_text(text=MESS_ADDED_TO_DB, reply_markup=reply_kb)
        await call.answer()
    else:
        intervals_set.symmetric_difference_update({call_item})
        await state.update_data(intervals_state=intervals_set)
        buttons_pack = [InlineKeyboardButton(text=f'{str(hour).zfill(2)}:00',
                                             callback_data=f'{CALL_CONFIG_SENDING_TIME}{str(hour).zfill(2)}:00')
                        for hour in range(7, 23)]

        buttons_pack = [update_button_with_check(button, CHECK_CONFIG_SENDING_TIME)
                        if button.text in intervals_set
                        else button
                        for button in buttons_pack]

        reply_kb = await keyboard_builder(menu_pack=menu_set_intervals,
                                          buttons_pack=buttons_pack,
                                          buttons_base_call=CALL_CONFIG_SENDING_TIME,
                                          buttons_cols=NUM_CONFIG_SENDING_TIME_COLS,
                                          buttons_rows=NUM_CONFIG_SENDING_TIME_ROWS,
                                          is_adding_confirm_button=True)

        await call.message.edit_text(text=MESS_MORE_CHOOSING, reply_markup=reply_kb)
        await call.answer()

