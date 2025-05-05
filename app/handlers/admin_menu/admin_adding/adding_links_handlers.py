from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.database.models import User, Link
from app.keyboards.menu_buttons import *
from app.common_settings import *

from app.keyboards.keyboard_builder import keyboard_builder, update_button_with_call_base
from app.utils.admin_utils import (message_answer, state_text_builder, add_item_in_aim_set_plus_plus)
from app.database.requests import (get_users_by_filters, get_groups_by_filters, set_link, get_links_by_filters,
                                   update_link_changing)
from app.handlers.admin_menu.states.state_executor import FSMExecutor
from app.handlers.admin_menu.states.state_params import InputStateParams
adding_link_router = Router()

class AddLink(StatesGroup):
    capture_link_changing = State()
    input_link_name_state = State()
    input_link_url_state = State()
    capture_groups_state = State()
    capture_users_state = State()
    capture_priority_state = State()
    confirmation_state = State()

menu_add_link = [
    [button_adding_menu_back, button_editing_menu_back, button_admin_menu, button_main_menu_back]
]

menu_add_link_with_changing = [
    [update_button_with_call_base(button_change_link_name, CALL_ADD_LINK),
     update_button_with_call_base(button_change_link_url, CALL_ADD_LINK)],
    [update_button_with_call_base(button_change_users, CALL_ADD_LINK),
     update_button_with_call_base(button_change_priority, CALL_ADD_LINK)],
    [button_adding_menu_back, button_admin_menu, button_main_menu_back]
]

# переход в меню добавления задания по схеме
@adding_link_router.callback_query(F.data == CALL_EDIT_LINK)
@adding_link_router.callback_query(F.data == CALL_ADD_LINK)
async def adding_first_state(call: CallbackQuery, state: FSMContext):
    # очистка стейта
    await state.clear()

    # задаем в стейт ид автора
    author = await get_users_by_filters(user_tg_id=call.from_user.id)
    await state.update_data(author_id=author.id)

    # начальные параметры стейта
    link_name_state = InputStateParams(self_state = AddLink.input_link_name_state,
                                       next_state = AddLink.input_link_url_state,
                                       call_base= CALL_ADD_LINK,
                                       main_mess= MESS_INPUT_LINK_NAME,
                                       menu_pack= menu_add_link,
                                       is_input=True,
                                       is_only_one=True)
    await state.update_data(input_link_name_state=link_name_state)

    link_url_state = InputStateParams(self_state=AddLink.input_link_url_state,
                                      next_state=AddLink.capture_groups_state,
                                      call_base=CALL_ADD_LINK,
                                      main_mess=MESS_INPUT_LINK_URL,
                                      menu_pack=menu_add_link,
                                      is_input=True,
                                      is_only_one=True)
    await state.update_data(input_link_url_state=link_url_state)

    groups_state = InputStateParams(self_state=AddLink.capture_groups_state,
                                            next_state=AddLink.capture_users_state,
                                            call_base=CALL_ADD_LINK,
                                            menu_pack=menu_add_link,
                                            is_can_be_empty=True)
    await groups_state.update_state_for_groups_capture()
    await state.update_data(capture_groups_state=groups_state)

    users_state = InputStateParams(self_state=AddLink.capture_users_state,
                                          next_state=AddLink.capture_priority_state,
                                          call_base=CALL_ADD_LINK,
                                          menu_pack=menu_add_link)
    await users_state.update_state_for_users_capture(users_filter='all')
    await state.update_data(capture_users_state=users_state)

    priority_state = InputStateParams(self_state=AddLink.capture_priority_state,
                                                next_state=AddLink.confirmation_state,
                                                call_base=CALL_ADD_LINK,
                                                menu_pack=menu_add_link,
                                                is_only_one=True)
    await priority_state.update_state_for_priority_capture()
    await state.update_data(capture_priority_state=priority_state)

    confirmation_state = InputStateParams(self_state = AddLink.confirmation_state,
                                                 call_base = CALL_ADD_LINK,
                                                 menu_pack= menu_add_link_with_changing,
                                                 is_last_state_with_changing_mode=True)
    await confirmation_state.update_state_for_confirmation_state()
    await state.update_data(confirmation_state=confirmation_state)

    # переход в первый стейт

    if call.data == CALL_EDIT_LINK:
        capture_link_changing = InputStateParams(
            self_state=AddLink.capture_link_changing,
            next_state=AddLink.confirmation_state,
            call_base=CALL_EDIT_LINK,
            menu_pack=menu_add_link,
            is_only_one=True)
        user : User = await get_users_by_filters(user_tg_id=call.from_user.id)
        await capture_link_changing.update_state_for_links_capture(links_filter='all')
        await state.update_data(capture_link_changing=capture_link_changing)
        first_state = capture_link_changing
    else:
        first_state = link_name_state


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

@adding_link_router.message(F.text, AddLink.capture_link_changing)
@adding_link_router.message(F.text, AddLink.input_link_name_state)
@adding_link_router.message(F.text, AddLink.input_link_url_state)
@adding_link_router.message(F.text, AddLink.capture_groups_state)
@adding_link_router.message(F.text, AddLink.capture_users_state)
@adding_link_router.message(F.text, AddLink.capture_priority_state)
async def admin_adding_link_capture(message: Message, state: FSMContext):
    # проверяем слово в базе данных
    # создаем экземпляр класса для обработки текущего состояния фсм
    current_fsm = FSMExecutor()
    # обрабатываем экземпляра класса, который анализирует наш колл и выдает сообщение и клавиатуру
    await current_fsm.execute(fsm_state=state, fsm_mess=message)

    state_text = await state_text_builder(state)
    message_text = state_text + '\n' + current_fsm.message_text
    await message_answer(source=message, message_text=message_text, reply_markup=current_fsm.reply_kb,
                         disable_web_page_preview=True)


@adding_link_router.callback_query(F.data.startswith(CALL_EDIT_LINK), AddLink.capture_link_changing)
@adding_link_router.callback_query(F.data.startswith(CALL_ADD_LINK), AddLink.capture_groups_state)
@adding_link_router.callback_query(F.data.startswith(CALL_ADD_LINK), AddLink.capture_users_state)
@adding_link_router.callback_query(F.data.startswith(CALL_ADD_LINK), AddLink.capture_priority_state)
async def set_scheme_capture_words_from_call(call: CallbackQuery, state: FSMContext):
    fsm_state_str_curr = await state.get_state()
    # создаем экземпляр класса для обработки текущего состояния фсм
    current_fsm = FSMExecutor()
    # обрабатываем экземпляра класса, который анализирует наш колл и выдает сообщение и клавиатуру
    await current_fsm.execute(fsm_state=state, fsm_call=call)
    # отвечаем заменой сообщения

    # специальный местный обработчик, который при работе с группами, добавляет сразу пользователей в стейт
    if fsm_state_str_curr == AddLink.capture_groups_state.state:
        groups_state: InputStateParams = await state.get_value('capture_groups_state')
        added_id = groups_state.set_of_items
        users_state: InputStateParams = await state.get_value('capture_users_state')
        new_user_set = set()
        for group_id in added_id:
            added_items = (await get_groups_by_filters(group_id=group_id)).users

            new_user_set = await add_item_in_aim_set_plus_plus(aim_set=new_user_set, added_item=added_items)
        users_state.set_of_items = new_user_set
        await state.update_data(capture_users_state=users_state)

    fsm_state_str_next = await state.get_state()

    if (fsm_state_str_curr == AddLink.capture_link_changing.state and
            fsm_state_str_next == AddLink.confirmation_state.state):
        capture_link_changing: InputStateParams = await state.get_value('capture_link_changing')
        link_id = int(list(capture_link_changing.set_of_items)[0])
        link : Link = await get_links_by_filters(link_id=link_id)

        input_link_name_state: InputStateParams = await state.get_value('input_link_name_state')
        input_link_name_state.input_text = link.name
        await state.update_data(input_link_name_state=input_link_name_state)

        input_link_url_state: InputStateParams = await state.get_value('input_link_url_state')
        input_link_url_state.input_text = link.link
        await state.update_data(input_link_url_state=input_link_url_state)

        users_state: InputStateParams = await state.get_value('capture_users_state')
        users_state.set_of_items = {int(x) for x in link.users.split(',')}
        await state.update_data(capture_users_state=users_state)

        capture_priority_state: InputStateParams = await state.get_value('capture_priority_state')
        capture_priority_state.set_of_items = {link.priority}
        await state.update_data(capture_priority_state=capture_priority_state)

        confirmation_state: InputStateParams = await state.get_value('confirmation_state')
        confirmation_state.call_base = CALL_EDIT_LINK
        # confirmation_state.main_mess = MESS_CHANGING
        await state.update_data(confirmation_state=confirmation_state)


    state_text = await state_text_builder(state)
    message_text = state_text + '\n' + current_fsm.message_text
    await call.message.edit_text(message_text, reply_markup=current_fsm.reply_kb, disable_web_page_preview=True)
    await call.answer()


# конечный обработчик всего стейта
@adding_link_router.callback_query(F.data.startswith(CALL_EDIT_LINK), AddLink.confirmation_state)
@adding_link_router.callback_query(F.data.startswith(CALL_ADD_LINK), AddLink.confirmation_state)
async def admin_adding_task_capture_confirmation_from_call(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека уровень
    confirm = call.data
    if call.data.startswith(CALL_ADD_LINK):
        confirm = confirm.replace(CALL_ADD_LINK, '')
    if call.data.startswith(CALL_EDIT_LINK):
        confirm = confirm.replace(CALL_EDIT_LINK, '')

    # уходим обратно если нужно что-то изменить
    if (confirm == CALL_CHANGING_LINK_NAME or confirm == CALL_CHANGING_LINK_URL or confirm == CALL_CHANGING_USERS
            or confirm == CALL_CHANGING_PRIRITY):

        confirmation_state: InputStateParams = await state.get_value('confirmation_state')

        if confirm == CALL_CHANGING_LINK_NAME:
            # при нажатии на изменение задаем следующий стейт элементов
            confirmation_state.next_state = AddLink.input_link_name_state
            # делаем так, чтобы в стейте добавления последний стейт (на изменения который) стал следующим
            input_link_name_state: InputStateParams = await state.get_value('input_link_name_state')
            input_link_name_state.next_state = AddLink.confirmation_state
            await state.update_data(input_link_name_state=input_link_name_state)

        elif confirm == CALL_CHANGING_LINK_URL:
            # при нажатии на изменение задаем следующий стейт элементов
            confirmation_state.next_state = AddLink.input_link_url_state
            # делаем так, чтобы в стейте добавления последний стейт (на изменения который) стал следующим
            input_link_url_state: InputStateParams = await state.get_value('input_link_url_state')
            input_link_url_state.next_state = AddLink.confirmation_state
            await state.update_data(input_link_url_state=input_link_url_state)

        elif confirm == CALL_CHANGING_USERS:
            # при нажатии на изменение задаем следующий стейт элементов
            confirmation_state.next_state = AddLink.capture_users_state
            # делаем так, чтобы в стейте добавления последний стейт (на изменения который) стал следующим
            capture_users_state: InputStateParams = await state.get_value('capture_users_state')
            capture_users_state.next_state = AddLink.confirmation_state
            await state.update_data(capture_users_state=capture_users_state)

        elif confirm == CALL_CHANGING_PRIRITY:
            # при нажатии на изменение задаем следующий стейт элементов
            confirmation_state.next_state = AddLink.capture_priority_state
            # делаем так, чтобы в стейте добавления последний стейт (на изменения который) стал следующим
            capture_priority_state: InputStateParams = await state.get_value('capture_priority_state')
            capture_priority_state.next_state = AddLink.confirmation_state
            await state.update_data(capture_priority_state=capture_priority_state)

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
        input_name_state: InputStateParams = await state.get_value('input_link_name_state')
        name_item = input_name_state.input_text

        input_url_state: InputStateParams = await state.get_value('input_link_url_state')
        url_item = input_url_state.input_text

        capture_users: InputStateParams = await state.get_value('capture_users_state')
        users_set = capture_users.set_of_items

        priority_state: InputStateParams = await state.get_value('capture_priority_state')
        priority_set = priority_state.set_of_items

        state_text = await state_text_builder(state)

        users_for_db = ','.join(map(str, list(users_set)))

        res = True

        for priority in priority_set:
            if call.data.startswith(CALL_ADD_LINK):
                res = res and await set_link(link_name=name_item,
                                             link_url=url_item,
                                             users=users_for_db,
                                             priority=priority)
            if call.data.startswith(CALL_EDIT_LINK):
                capture_link_changing: InputStateParams = await state.get_value('capture_link_changing')
                link_id = int(list(capture_link_changing.set_of_items)[0])
                res = res and await update_link_changing(link_id = link_id,
                                             link_name=name_item,
                                             link_url=url_item,
                                             users=users_for_db,
                                             priority=priority)

        message_text = f'----- ----- -----\n{state_text}----- ----- -----\n'

        if res:
            message_text += MESS_ADDED_TO_DB
        else:
            message_text += MESS_ERROR_ADDED_TO_DB

        reply_kb = await keyboard_builder(menu_pack=menu_add_link, buttons_base_call="")

        await call.message.edit_text(message_text, reply_markup=reply_kb)
        await call.answer()

