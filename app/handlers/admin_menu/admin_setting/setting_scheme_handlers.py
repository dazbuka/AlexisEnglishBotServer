from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

from app.keyboards.menu_buttons import *
from app.handlers.common_settings import *

from app.database.requests import get_users_by_filters, get_groups_by_filters
from app.utils.admin_utils import message_answer, add_item_in_aim_set_plus_plus
from app.utils.admin_utils import state_text_builder
from app.database.requests import get_medias_by_filters, set_task
from app.handlers.admin_menu.states.state_executor import FSMExecutor
from app.handlers.admin_menu.states.state_params import InputStateParams
from app.keyboards.keyboard_builder import keyboard_builder, update_button_with_call_base

setting_scheme_router = Router()

class SetScheme(StatesGroup):
    author_id = State() # автор который назначает задание - ид
    capture_words_state = State()
    capture_groups_state = State()
    capture_users_state = State()
    capture_dates_state = State()
    confirmation_state = State() # стейт обрабатывающий конечное подтверждение ввода

menu_set_scheme = [
    [button_setting_menu_back, button_admin_menu, button_main_menu_back]
]

menu_set_scheme_with_changing = [
    [update_button_with_call_base(button_change_words, CALL_SET_SCHEME),
     update_button_with_call_base(button_change_users, CALL_SET_SCHEME),
     update_button_with_call_base(button_change_dates, CALL_SET_SCHEME)],
    [button_setting_menu_back, button_admin_menu, button_main_menu_back]
]

# переход в меню добавления задания по схеме
@setting_scheme_router.callback_query(F.data == CALL_SET_SCHEME)
async def setting_scheme_first_state(call: CallbackQuery, state: FSMContext):
    # очистка стейта
    await state.clear()

    # задаем в стейт ид автора
    author = await get_users_by_filters(user_tg_id=call.from_user.id)
    await state.update_data(author_id=author.id)

    words_state = InputStateParams(self_state = SetScheme.capture_words_state,
                                          next_state = SetScheme.capture_groups_state,
                                          call_base= CALL_SET_SCHEME,
                                          menu_pack= menu_set_scheme)
    await words_state.update_state_for_words_capture(words_filter='all')
    await state.update_data(capture_words_state=words_state)

    # здесь добавлен парамент из кэн би эмпти - можно проходить дальше если пустой

    groups_state = InputStateParams(self_state=SetScheme.capture_groups_state,
                                            next_state=SetScheme.capture_users_state,
                                            call_base=CALL_SET_SCHEME,
                                            menu_pack=menu_set_scheme,
                                            is_can_be_empty=True)
    await groups_state.update_state_for_groups_capture()
    await state.update_data(capture_groups_state=groups_state)

    users_state = InputStateParams(self_state=SetScheme.capture_users_state,
                                          next_state=SetScheme.capture_dates_state,
                                          call_base=CALL_SET_SCHEME,
                                          menu_pack=menu_set_scheme)
    await users_state.update_state_for_users_capture(users_filter='all')
    await state.update_data(capture_users_state=users_state)

    dates_state = InputStateParams(self_state=SetScheme.capture_dates_state,
                                          next_state=SetScheme.confirmation_state,
                                          call_base=CALL_SET_SCHEME,
                                          menu_pack=menu_set_scheme,
                                          is_only_one = True)
    await dates_state.update_state_for_dates_capture()
    await state.update_data(capture_dates_state=dates_state)

    confirmation_state = InputStateParams(self_state = SetScheme.confirmation_state,
                                                 call_base = CALL_SET_SCHEME,
                                                 menu_pack= menu_set_scheme_with_changing,
                                                 is_last_state_with_changing_mode=True)
    await confirmation_state.update_state_for_confirmation_state()
    await state.update_data(confirmation_state=confirmation_state)

    first_state = words_state

    # переход в первый стейт
    await state.set_state(first_state.self_state)
    # формируем сообщение, меню, клавиатуру и выводим их
    reply_kb = await keyboard_builder(menu_pack=first_state.menu_pack,
                                      buttons_pack=first_state.buttons_pack,
                                      buttons_base_call=first_state.call_base,
                                      buttons_cols=first_state.buttons_cols,
                                      buttons_rows=first_state.buttons_rows,
                                      is_adding_confirm_button=not first_state.is_only_one)

    state_text = await state_text_builder(state)
    message_text = state_text + '\n' + first_state.main_mess
    await call.message.edit_text(text=message_text, reply_markup=reply_kb)

    # await call.message.edit_text(message_text, reply_markup=reply_kb)
    await call.answer()



# цикличные хендлеры захвата слов, пользователей и др.
@setting_scheme_router.callback_query(F.data.startswith(CALL_SET_SCHEME), SetScheme.capture_words_state)
@setting_scheme_router.callback_query(F.data.startswith(CALL_SET_SCHEME), SetScheme.capture_groups_state)
@setting_scheme_router.callback_query(F.data.startswith(CALL_SET_SCHEME), SetScheme.capture_users_state)
@setting_scheme_router.callback_query(F.data.startswith(CALL_SET_SCHEME), SetScheme.capture_dates_state)
async def set_scheme_capture_words_from_call(call: CallbackQuery, state: FSMContext):
    fsm_state_str_curr = await state.get_state()
    # создаем экземпляр класса для обработки текущего состояния фсм
    current_fsm = FSMExecutor()
    # обрабатываем экземпляра класса, который анализирует наш колл и выдает сообщение и клавиатуру
    await current_fsm.execute(fsm_state=state, fsm_call=call)

    # специальный местный обработчик, который при работе с группами, добавляет сразу пользователей в стейт
    if fsm_state_str_curr == SetScheme.capture_groups_state.state:
        groups_state : InputStateParams  = await state.get_value('capture_groups_state')
        added_id = groups_state.set_of_items
        users_state : InputStateParams = await state.get_value('capture_users_state')
        new_user_set = set()
        for group_id in added_id:
            added_items = (await get_groups_by_filters(group_id=group_id)).users

            new_user_set = await add_item_in_aim_set_plus_plus(aim_set=new_user_set, added_item=added_items)
        users_state.set_of_items = new_user_set
        await state.update_data(capture_users_state=users_state)


    # отвечаем заменой сообщения
    state_text = await state_text_builder(state)
    message_text = state_text + '\n' + current_fsm.message_text
    await call.message.edit_text(message_text, reply_markup=current_fsm.reply_kb)
    await call.answer()


# хендлеры поиска слов, введенных с клавиатуры
@setting_scheme_router.message(F.text, SetScheme.capture_words_state)
@setting_scheme_router.message(F.text, SetScheme.capture_groups_state)
@setting_scheme_router.message(F.text, SetScheme.capture_users_state)
@setting_scheme_router.message(F.text, SetScheme.capture_dates_state)
async def set_scheme_capture_words_from_message(message: Message, state: FSMContext):
    current_fsm = FSMExecutor()
    # обрабатываем экземпляра класса, который анализирует наш ввод и выдает сообщение и клавиатуру
    await current_fsm.execute(fsm_state=state, fsm_mess=message)
    state_text = await state_text_builder(state)
    message_text = state_text + '\n' + current_fsm.message_text
    await message_answer(source=message, message_text=message_text, reply_markup=current_fsm.reply_kb)


# конечный обработчик всего стейта
@setting_scheme_router.callback_query(F.data.startswith(CALL_SET_SCHEME), SetScheme.confirmation_state)
async def admin_adding_task_capture_confirmation_from_call(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека уровень
    confirm = call.data.replace(CALL_SET_SCHEME, '')
    # уходим обратно если нужно что-то изменить

    if confirm == CALL_CHANGING_WORDS or confirm == CALL_CHANGING_USERS or confirm == CALL_CHANGING_DATES:
        confirmation_state: InputStateParams = await state.get_value('confirmation_state')

        if confirm == CALL_CHANGING_WORDS:
            # при нажатии на изменение задаем следующий стейт элементов
            confirmation_state.next_state = SetScheme.capture_words_state
            # делаем так, чтобы в стейте добавления последний стейт (на изменения который) стал следующим
            capture_words: InputStateParams = await state.get_value('capture_words_state')
            capture_words.next_state = SetScheme.confirmation_state
            await state.update_data(capture_words_state=capture_words)

        elif confirm == CALL_CHANGING_USERS:
            # при нажатии на изменение задаем следующий стейт элементов
            confirmation_state.next_state = SetScheme.capture_users_state
            # делаем так, чтобы в стейте добавления последний стейт (на изменения который) стал следующим
            capture_users: InputStateParams = await state.get_value('capture_users_state')
            capture_users.next_state = SetScheme.confirmation_state
            await state.update_data(capture_users_state=capture_users)

        elif confirm == CALL_CHANGING_DATES:
            # при нажатии на изменение задаем следующий стейт элементов
            confirmation_state.next_state = SetScheme.capture_dates_state
            # делаем так, чтобы в стейте добавления последний стейт (на изменения который) стал следующим
            capture_dates: InputStateParams = await state.get_value('capture_dates_state')
            capture_dates.next_state = SetScheme.confirmation_state
            await state.update_data(capture_dates_state=capture_dates)

        await state.update_data(confirmation_state=confirmation_state)
        current_fsm = FSMExecutor()
        await current_fsm.execute(state, call)
        state_text = await state_text_builder(state)
        message_text = state_text + '\n' + current_fsm.message_text
        await call.message.edit_text(message_text, reply_markup=current_fsm.reply_kb)
        await call.answer()

    elif confirm == CALL_CONFIRM:
        # основной обработчик, запись в бд
        author_id = await state.get_value('author_id')

        capture_words: InputStateParams = await state.get_value('capture_words_state')
        words_set = capture_words.set_of_items

        capture_users: InputStateParams = await state.get_value('capture_users_state')
        users_set = capture_users.set_of_items

        capture_dates: InputStateParams = await state.get_value('capture_dates_state')
        dates_set = capture_dates.set_of_items

        state_text = await state_text_builder(state)

        res = True
        for word in words_set:
            medias = await get_medias_by_filters(word_id=word)
            for media in medias:
                for date in dates_set:
                    assign_date = datetime.strptime(date, "%d.%m.%Y") + timedelta(media.study_day - 1)
                    task_day = datetime.combine(assign_date, datetime.now().time())
                    for user in users_set:
                        res = res and await set_task(user_id=user,
                                                        media_id=media.id,
                                                        task_time=task_day,
                                                        author_id=author_id)

        message_text = f'----- ----- -----\n{state_text}----- ----- -----\n'

        if res:
            message_text += MESS_ADDED_TO_DB
        else:
            message_text += MESS_ERROR_ADDED_TO_DB

        reply_kb = await keyboard_builder(menu_pack=menu_set_scheme, buttons_base_call="")

        await call.message.edit_text(message_text, reply_markup=reply_kb)
        await call.answer()


