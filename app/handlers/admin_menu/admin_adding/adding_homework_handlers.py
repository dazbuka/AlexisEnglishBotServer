from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from datetime import datetime

from app.keyboards.menu_buttons import *
from app.common_settings import *

from app.keyboards.keyboard_builder import keyboard_builder, update_button_with_call_base
from app.utils.admin_utils import (message_answer, state_text_builder, add_item_in_aim_set_plus_plus)
from app.database.requests import (get_users_by_filters, get_groups_by_filters, set_homework, get_homeworks_by_filters,
                                   update_homework_editing)


from app.handlers.admin_menu.states.state_executor import FSMExecutor
from app.handlers.admin_menu.states.state_params import InputStateParams

adding_homework_router = Router()

class AddHomework(StatesGroup):
    author_id = State()  # автор который назначает задание - ид
    input_homework_state = State()
    capture_homeworks_for_edit_state = State()
    capture_groups_state = State()
    capture_users_state = State()
    capture_dates_state = State()
    confirmation_state = State()

menu_add_homework = [
    [button_adding_menu_back, button_editing_menu_back, button_admin_menu_back, button_main_menu_back]
]

menu_add_homework_with_changing = [
    [update_button_with_call_base(button_change_homework, CALL_ADD_HOMEWORK),
     update_button_with_call_base(button_change_users, CALL_ADD_HOMEWORK),
     update_button_with_call_base(button_change_dates, CALL_ADD_HOMEWORK)],
    [button_adding_menu_back, button_editing_menu_back, button_admin_menu_back, button_main_menu_back]
]

# входим в хендлер по добавление или редактированию
@adding_homework_router.callback_query(F.data == CALL_EDIT_HOMEWORK)
@adding_homework_router.callback_query(F.data == CALL_ADD_HOMEWORK)
async def adding_first_state(call: CallbackQuery, state: FSMContext):
    # очистка стейта
    await state.clear()
    # задаем в стейт ид автора
    author = await get_users_by_filters(user_tg_id=call.from_user.id)
    await state.update_data(author_id=author.id)
    # начальные параметры стейта
    input_homework_state = InputStateParams(self_state = AddHomework.input_homework_state,
                                            next_state = AddHomework.capture_groups_state,
                                            call_base= CALL_ADD_HOMEWORK,
                                            main_mess= MESS_INPUT_HOMEWORK,
                                            menu_pack= menu_add_homework,
                                            is_input=True,
                                            is_only_one = True)
    await state.update_data(input_homework_state=input_homework_state)

    groups_state = InputStateParams(self_state=AddHomework.capture_groups_state,
                                            next_state=AddHomework.capture_users_state,
                                            call_base=CALL_ADD_HOMEWORK,
                                            menu_pack=menu_add_homework,
                                            is_can_be_empty=True)
    await groups_state.update_state_for_groups_capture()
    await state.update_data(capture_groups_state=groups_state)

    users_state = InputStateParams(self_state=AddHomework.capture_users_state,
                                          next_state=AddHomework.capture_dates_state,
                                          call_base=CALL_ADD_HOMEWORK,
                                          menu_pack=menu_add_homework)
    await users_state.update_state_for_users_capture(users_filter='all')
    await state.update_data(capture_users_state=users_state)

    dates_state = InputStateParams(self_state=AddHomework.capture_dates_state,
                                          next_state=AddHomework.confirmation_state,
                                          call_base=CALL_ADD_HOMEWORK,
                                          menu_pack=menu_add_homework,
                                          is_only_one=True)
    await dates_state.update_state_for_dates_capture()
    await state.update_data(capture_dates_state=dates_state)

    confirmation_state = InputStateParams(self_state = AddHomework.confirmation_state,
                                                 call_base = CALL_ADD_HOMEWORK,
                                                 menu_pack= menu_add_homework_with_changing,
                                                 is_last_state_with_changing_mode=True)
    await confirmation_state.update_state_for_confirmation_state()
    await state.update_data(confirmation_state=confirmation_state)


    # переход в первый стейт

    if call.data == CALL_EDIT_HOMEWORK:
        capture_homeworks_for_edit_state = InputStateParams(
            self_state=AddHomework.capture_homeworks_for_edit_state,
            next_state=AddHomework.confirmation_state,
            call_base=CALL_EDIT_HOMEWORK,
            menu_pack=menu_add_homework,
            is_only_one=True)
        await capture_homeworks_for_edit_state.update_state_for_homeworks_capture()
        await state.update_data(capture_homeworks_for_edit_state=capture_homeworks_for_edit_state)
        first_state = capture_homeworks_for_edit_state
    else:
        first_state = input_homework_state

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

@adding_homework_router.message(F.text, AddHomework.capture_homeworks_for_edit_state)
@adding_homework_router.message(F.text, AddHomework.input_homework_state)
@adding_homework_router.message(F.text, AddHomework.capture_groups_state)
@adding_homework_router.message(F.text, AddHomework.capture_users_state)
@adding_homework_router.message(F.text, AddHomework.capture_dates_state)
async def admin_adding_homework_capture(message: Message, state: FSMContext):
    # проверяем слово в базе данных
    # создаем экземпляр класса для обработки текущего состояния фсм
    current_fsm = FSMExecutor()
    # обрабатываем экземпляра класса, который анализирует наш колл и выдает сообщение и клавиатуру
    await current_fsm.execute(fsm_state=state, fsm_mess=message)

    state_text = await state_text_builder(state)
    message_text = state_text + '\n' + current_fsm.message_text
    await message_answer(source=message, message_text=message_text, reply_markup=current_fsm.reply_kb)



@adding_homework_router.callback_query(F.data.startswith(CALL_EDIT_HOMEWORK), AddHomework.capture_homeworks_for_edit_state)
@adding_homework_router.callback_query(F.data.startswith(CALL_ADD_HOMEWORK), AddHomework.capture_groups_state)
@adding_homework_router.callback_query(F.data.startswith(CALL_ADD_HOMEWORK), AddHomework.capture_users_state)
@adding_homework_router.callback_query(F.data.startswith(CALL_ADD_HOMEWORK), AddHomework.capture_dates_state)
async def set_scheme_capture_words_from_call(call: CallbackQuery, state: FSMContext):
    fsm_state_str_curr = await state.get_state()
    # создаем экземпляр класса для обработки текущего состояния фсм
    current_fsm = FSMExecutor()
    # обрабатываем экземпляра класса, который анализирует наш колл и выдает сообщение и клавиатуру
    await current_fsm.execute(fsm_state=state, fsm_call=call)
    # отвечаем заменой сообщения


    # специальный местный обработчик, который при работе с группами, добавляет сразу пользователей в стейт
    if fsm_state_str_curr == AddHomework.capture_groups_state.state:
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

    if (fsm_state_str_curr == AddHomework.capture_homeworks_for_edit_state.state and
            fsm_state_str_next == AddHomework.confirmation_state.state):
        capture_homeworks_state: InputStateParams = await state.get_value('capture_homeworks_for_edit_state')
        homework_id_set = capture_homeworks_state.set_of_items
        homework_id_list = list(homework_id_set)
        homework_id = int(homework_id_list[0])
        homework = await get_homeworks_by_filters(homework_id_new=homework_id, actual=False)

        await state.update_data(author_id=homework.author_id)

        edited_homework = homework.hometask
        input_homework_state: InputStateParams = await state.get_value('input_homework_state')
        input_homework_state.input_text = edited_homework
        await state.update_data(input_homework_state=input_homework_state)

        edited_users = {int(x) for x in homework.users.split(',')}
        users_state: InputStateParams = await state.get_value('capture_users_state')
        users_state.set_of_items = edited_users
        await state.update_data(capture_users_state=users_state)

        edited_date = homework.time.strftime("%d.%m.%Y")
        dates_state: InputStateParams = await state.get_value('capture_dates_state')
        dates_state.set_of_items.add(edited_date)
        await state.update_data(capture_dates_state=dates_state)

        confirmation_state: InputStateParams = await state.get_value('confirmation_state')
        confirmation_state.call_base = CALL_EDIT_HOMEWORK
        confirmation_state.main_mess = MESS_CHANGING
        await state.update_data(confirmation_state=confirmation_state)


    state_text = await state_text_builder(state)
    message_text = state_text + '\n' + current_fsm.message_text
    await call.message.edit_text(message_text, reply_markup=current_fsm.reply_kb)
    await call.answer()


# конечный обработчик всего стейта
@adding_homework_router.callback_query(F.data.startswith(CALL_EDIT_HOMEWORK), AddHomework.confirmation_state)
@adding_homework_router.callback_query(F.data.startswith(CALL_ADD_HOMEWORK), AddHomework.confirmation_state)
async def admin_adding_task_capture_confirmation_from_call(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека уровень
    confirm = call.data
    if call.data.startswith(CALL_ADD_HOMEWORK):
        confirm = confirm.replace(CALL_ADD_HOMEWORK, '')
    if call.data.startswith(CALL_EDIT_HOMEWORK):
        confirm = confirm.replace(CALL_EDIT_HOMEWORK, '')

    # уходим обратно если нужно что-то изменить
    if confirm == CALL_CHANGING_USERS or confirm == CALL_CHANGING_DATES or confirm == CALL_CHANGING_HOMEWORK:

        confirmation_state: InputStateParams = await state.get_value('confirmation_state')

        if confirm == CALL_CHANGING_HOMEWORK:
            # при нажатии на изменение задаем следующий стейт элементов
            confirmation_state.next_state = AddHomework.input_homework_state
            # делаем так, чтобы в стейте добавления последний стейт (на изменения который) стал следующим
            input_homework_state: InputStateParams = await state.get_value('input_homework_state')
            input_homework_state.next_state = AddHomework.confirmation_state
            await state.update_data(input_homework_state=input_homework_state)

        elif confirm == CALL_CHANGING_USERS:
            # при нажатии на изменение задаем следующий стейт элементов
            confirmation_state.next_state = AddHomework.capture_users_state
            # делаем так, чтобы в стейте добавления последний стейт (на изменения который) стал следующим
            capture_users_state: InputStateParams = await state.get_value('capture_users_state')
            capture_users_state.next_state = AddHomework.confirmation_state
            await state.update_data(capture_users_state=capture_users_state)

        elif confirm == CALL_CHANGING_DATES:
            # при нажатии на изменение задаем следующий стейт элементов
            confirmation_state.next_state = AddHomework.capture_dates_state
            # делаем так, чтобы в стейте добавления последний стейт (на изменения который) стал следующим
            capture_dates_state: InputStateParams = await state.get_value('capture_dates_state')
            capture_dates_state.next_state = AddHomework.confirmation_state
            await state.update_data(capture_dates_state=capture_dates_state)

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
        author_id = await state.get_value('author_id')

        input_homework: InputStateParams = await state.get_value('input_homework_state')
        homework_item = input_homework.input_text




        capture_users: InputStateParams = await state.get_value('capture_users_state')
        users_set = capture_users.set_of_items

        capture_dates: InputStateParams = await state.get_value('capture_dates_state')
        dates_set = capture_dates.set_of_items

        state_text = await state_text_builder(state)



        users_for_db = ','.join(map(str, list(users_set)))

        res = True

        for date_item in dates_set:
            date_format = datetime.strptime(date_item, "%d.%m.%Y")
            date_for_db = datetime.combine(date_format, datetime.now().time())

            if call.data.startswith(CALL_ADD_HOMEWORK):
                res = res and await set_homework(hometask=homework_item,
                                                 homework_date=date_for_db,
                                                 author_id=author_id,
                                                 users=users_for_db)
            if call.data.startswith(CALL_EDIT_HOMEWORK):
                capture_edited_homework: InputStateParams = await state.get_value('capture_homeworks_for_edit_state')
                edited_homeworks_set = capture_edited_homework.set_of_items
                homework_id_list = list(edited_homeworks_set)
                homework_id = int(homework_id_list[0])
                res = res and await update_homework_editing(homework_id=homework_id,
                                                            hometask=homework_item,
                                                            homework_date=date_for_db,
                                                            author_id=author_id,
                                                            users=users_for_db)




        message_text = f'----- ----- -----\n{state_text}----- ----- -----\n'

        if res:
            message_text += MESS_ADDED_TO_DB
        else:
            message_text += MESS_ERROR_ADDED_TO_DB

        reply_kb = await keyboard_builder(menu_pack=menu_add_homework, buttons_base_call="")

        await call.message.edit_text(message_text, reply_markup=reply_kb)
        await call.answer()

