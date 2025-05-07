from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.database.models import Group
from app.keyboards.menu_buttons import *
from app.common_settings import *

from app.keyboards.keyboard_builder import keyboard_builder, update_button_with_call_base
from app.admin_utils import message_answer, state_text_builder
from app.database.requests import set_group, get_groups_by_filters, update_group_editing
from app.handlers.states.loop_state_executor import FSMExecutor
from app.handlers.states.loop_state_params import (InputStateParams)
adding_group_router = Router()

class AddGroup(StatesGroup):
    capture_group_changing = State()
    input_group_state = State()
    capture_users_state = State()
    capture_levels_state = State()
    confirmation_state = State()

menu_add_group = [
    [button_adding_menu_back, button_editing_menu_back, button_admin_menu_back, button_main_menu_back]
]

menu_add_group_with_changing = [
    [update_button_with_call_base(button_change_group, CALL_ADD_GROUP),
     update_button_with_call_base(button_change_users, CALL_ADD_GROUP),
     update_button_with_call_base(button_change_levels, CALL_ADD_GROUP)],
    [button_adding_menu_back, button_editing_menu_back, button_admin_menu_back, button_main_menu_back]
]

# переход в меню добавления задания по схеме
@adding_group_router.callback_query(F.data == CALL_EDIT_GROUP)
@adding_group_router.callback_query(F.data == CALL_ADD_GROUP)
async def adding_first_state(call: CallbackQuery, state: FSMContext):
    # очистка стейта
    await state.clear()

    # начальные параметры стейта
    input_group_state = InputStateParams(self_state = AddGroup.input_group_state,
                                   next_state = AddGroup.capture_users_state,
                                   call_base= CALL_ADD_GROUP,
                                   main_mess= MESS_INPUT_GROUP,
                                   menu_pack= menu_add_group,
                                   is_input=True,
                                   is_only_one=True)
    await state.update_data(input_group_state=input_group_state)

    users_state = InputStateParams(self_state=AddGroup.capture_users_state,
                                          next_state=AddGroup.capture_levels_state,
                                          call_base= CALL_ADD_GROUP,
                                          menu_pack=menu_add_group)
    await users_state.update_state_for_users_capture(users_filter='all')
    await state.update_data(capture_users_state=users_state)


    levels_state = InputStateParams(self_state=AddGroup.capture_levels_state,
                                            next_state=AddGroup.confirmation_state,
                                            call_base=CALL_ADD_GROUP,
                                            menu_pack=menu_add_group,
                                            is_only_one=True)
    await levels_state.update_state_for_level_capture()
    await state.update_data(capture_levels_state=levels_state)


    confirmation_state = InputStateParams(self_state = AddGroup.confirmation_state,
                                                 menu_pack= menu_add_group_with_changing,
                                                 call_base=CALL_ADD_GROUP,
                                                 is_last_state_with_changing_mode=True)
    await confirmation_state.update_state_for_confirmation_state()
    await state.update_data(confirmation_state=confirmation_state)

    if call.data == CALL_EDIT_GROUP:
        capture_group_changing = InputStateParams(
            self_state=AddGroup.capture_group_changing,
            next_state=AddGroup.confirmation_state,
            call_base=CALL_EDIT_GROUP,
            menu_pack=menu_add_group,
            is_only_one=True)
        await capture_group_changing.update_state_for_groups_capture()
        await state.update_data(capture_group_changing=capture_group_changing)
        first_state = capture_group_changing
    else:
        first_state = input_group_state


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
    await call.answer()

@adding_group_router.message(F.text, AddGroup.capture_group_changing)
@adding_group_router.message(F.text, AddGroup.input_group_state)
@adding_group_router.message(F.text, AddGroup.capture_users_state)
@adding_group_router.message(F.text, AddGroup.capture_levels_state)
async def admin_adding_group_capture(message: Message, state: FSMContext):
    # проверяем слово в базе данных
    fsm_state_str = await state.get_state()
    # проверяем группу в базе данных
    if fsm_state_str == AddGroup.input_group_state.state:
        input_group_state: InputStateParams = await state.get_value('input_group_state')
        capture_group_changing: InputStateParams = await state.get_value('capture_group_changing')
        input_group = message.text.lower()
        groups = await get_groups_by_filters(name=input_group)
        if groups:
            input_group_state.next_state = AddGroup.input_group_state
            input_group_state.main_mess = MESS_INPUT_GROUP_ALREADY_EXIST
        elif capture_group_changing:
            input_group_state.next_state = AddGroup.confirmation_state
            input_group_state.main_mess = MESS_INPUT_GROUP
        else:
            input_group_state.next_state = AddGroup.capture_users_state
            input_group_state.main_mess = MESS_INPUT_GROUP

        await state.update_data(input_group_state=input_group_state)

    # создаем экземпляр класса для обработки текущего состояния фсм
    current_fsm = FSMExecutor()
    # обрабатываем экземпляра класса, который анализирует наш колл и выдает сообщение и клавиатуру
    await current_fsm.execute(fsm_state=state, fsm_mess=message)

    state_text = await state_text_builder(state)
    message_text = state_text + '\n' + current_fsm.message_text
    await message_answer(source=message, message_text=message_text, reply_markup=current_fsm.reply_kb)


@adding_group_router.callback_query(F.data.startswith(CALL_EDIT_GROUP), AddGroup.capture_group_changing)
@adding_group_router.callback_query(F.data.startswith(CALL_ADD_GROUP), AddGroup.capture_users_state)
@adding_group_router.callback_query(F.data.startswith(CALL_ADD_GROUP), AddGroup.capture_levels_state)
async def set_scheme_capture_words_from_call(call: CallbackQuery, state: FSMContext):
    fsm_state_str_curr = await state.get_state()
    # создаем экземпляр класса для обработки текущего состояния фсм
    current_fsm = FSMExecutor()
    # обрабатываем экземпляра класса, который анализирует наш колл и выдает сообщение и клавиатуру
    await current_fsm.execute(fsm_state=state, fsm_call=call)
    # отвечаем заменой сообщения

    fsm_state_str_next = await state.get_state()

    if (fsm_state_str_curr == AddGroup.capture_group_changing.state and
            fsm_state_str_next == AddGroup.confirmation_state.state):
        capture_group_state: InputStateParams = await state.get_value('capture_group_changing')
        group_id = int(list(capture_group_state.set_of_items)[0])
        group : Group = await get_groups_by_filters(group_id=group_id)

        if group.name:
            input_group_state: InputStateParams = await state.get_value('input_group_state')
            input_group_state.input_text = group.name
            await state.update_data(input_group_state=input_group_state)

        if group.users:
            users_state: InputStateParams = await state.get_value('capture_users_state')
            users_state.set_of_items = {int(x) for x in group.users.split(',')}
            await state.update_data(capture_users_state=users_state)

        if group.level:
            levels_state: InputStateParams = await state.get_value('capture_levels_state')
            levels_state.set_of_items = {group.level}
            await state.update_data(capture_levels_state=levels_state)

        confirmation_state: InputStateParams = await state.get_value('confirmation_state')
        confirmation_state.call_base = CALL_EDIT_GROUP
        # confirmation_state.main_mess = MESS_ADD_ENDING
        await state.update_data(confirmation_state=confirmation_state)

    state_text = await state_text_builder(state)
    message_text = state_text + '\n' + current_fsm.message_text
    await call.message.edit_text(message_text, reply_markup=current_fsm.reply_kb)
    await call.answer()


# конечный обработчик всего стейта
@adding_group_router.callback_query(F.data.startswith(CALL_EDIT_GROUP), AddGroup.confirmation_state)
@adding_group_router.callback_query(F.data.startswith(CALL_ADD_GROUP), AddGroup.confirmation_state)
async def admin_adding_task_capture_confirmation_from_call(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека уровень
    confirm = call.data
    if call.data.startswith(CALL_ADD_GROUP):
        confirm = confirm.replace(CALL_ADD_GROUP, '')
    if call.data.startswith(CALL_EDIT_GROUP):
        confirm = confirm.replace(CALL_EDIT_GROUP, '')


    # уходим обратно если нужно что-то изменить
    if (confirm == CALL_CHANGING_USERS or confirm == CALL_CHANGING_LEVELS or confirm == CALL_CHANGING_GROUP):

        confirmation_state: InputStateParams = await state.get_value('confirmation_state')

        if confirm == CALL_CHANGING_GROUP:
            # при нажатии на изменение задаем следующий стейт элементов
            confirmation_state.next_state = AddGroup.input_group_state
            # делаем так, чтобы в стейте добавления последний стейт (на изменения который) стал следующим
            input_group_state: InputStateParams = await state.get_value('input_group_state')
            input_group_state.next_state = AddGroup.confirmation_state
            await state.update_data(input_group_state=input_group_state)

        elif confirm == CALL_CHANGING_USERS:
            # при нажатии на изменение задаем следующий стейт элементов
            confirmation_state.next_state = AddGroup.capture_users_state
            # делаем так, чтобы в стейте добавления последний стейт (на изменения который) стал следующим
            capture_users_state: InputStateParams = await state.get_value('capture_users_state')
            capture_users_state.next_state = AddGroup.confirmation_state
            await state.update_data(capture_users_state=capture_users_state)

        elif confirm == CALL_CHANGING_LEVELS:
            # при нажатии на изменение задаем следующий стейт элементов
            confirmation_state.next_state = AddGroup.capture_levels_state
            # делаем так, чтобы в стейте добавления последний стейт (на изменения который) стал следующим
            capture_levels_state: InputStateParams = await state.get_value('capture_levels_state')
            capture_levels_state.next_state = AddGroup.confirmation_state
            await state.update_data(capture_levels_state=capture_levels_state)

        await state.update_data(confirmation_state=confirmation_state)
        current_fsm = FSMExecutor()
        await current_fsm.execute(state, call)
        state_text = await state_text_builder(state)
        message_text = state_text + '\n' + current_fsm.message_text
        await call.message.edit_text(message_text, reply_markup=current_fsm.reply_kb)
        await call.answer()

    # обрабатываем ввод, если все ок и нажато подтверждение
    elif confirm == CALL_CONFIRM:

        # основной обработчик, запись в бд
        input_group: InputStateParams = await state.get_value('input_group_state')
        group_item = input_group.input_text

        capture_users: InputStateParams = await state.get_value('capture_users_state')
        users_set = capture_users.set_of_items

        capture_levels: InputStateParams = await state.get_value('capture_levels_state')
        levels_set = capture_levels.set_of_items

        state_text = await state_text_builder(state)

        res = True

        users_for_db = ','.join(map(str, list(users_set)))

        for level in levels_set:
            if call.data.startswith(CALL_ADD_GROUP):
                res = res and await set_group(name=group_item,
                                              users=users_for_db,
                                              level=level)
            if call.data.startswith(CALL_EDIT_GROUP):
                capture_group_changing: InputStateParams = await state.get_value('capture_group_changing')
                group_id = int(list(capture_group_changing.set_of_items)[0])
                res = res and await update_group_editing(group_id=group_id,
                                                         name=group_item,
                                                         users=users_for_db,
                                                         level=level)


        message_text = f'----- ----- -----\n{state_text}----- ----- -----\n'

        if res:
            message_text += MESS_ADDED_TO_DB
        else:
            message_text += MESS_ERROR_ADDED_TO_DB

        reply_kb = await keyboard_builder(menu_pack=menu_add_group, buttons_base_call="")

        await call.message.edit_text(message_text, reply_markup=reply_kb)
        await call.answer()

