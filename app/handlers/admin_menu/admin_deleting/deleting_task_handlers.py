from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.database.models import Group
from app.keyboards.menu_buttons import *
from app.common_settings import *

from app.keyboards.keyboard_builder import keyboard_builder, update_button_with_call_base
from app.admin_utils import message_answer, state_text_builder
from app.database.requests import set_group, delete_task_from_db
from app.handlers.states.loop_state_executor import FSMExecutor
from app.handlers.states.loop_state_params import (InputStateParams)

deleting_task_router = Router()

class DeletingTask(StatesGroup):
    capture_users_state = State()
    capture_tasks_state = State()
    confirmation_state = State()

menu_delete_task = [
    [button_deleting_menu_back, button_admin_menu_back, button_main_menu_back]
]

# переход в меню добавления задания по схеме
@deleting_task_router.callback_query(F.data == CALL_DELETE_TASK)
async def deleting_first_state(call: CallbackQuery, state: FSMContext):
    # очистка стейта
    await state.clear()

    # начальные параметры стейта
    users_state = InputStateParams(self_state=DeletingTask.capture_users_state,
                                   next_state=DeletingTask.capture_tasks_state,
                                   call_base= CALL_DELETE_TASK,
                                   menu_pack=menu_delete_task,
                                   is_only_one=True)
    await users_state.update_state_for_users_capture(users_filter='all')
    await state.update_data(capture_users_state=users_state)

    tasks_state = InputStateParams(self_state=DeletingTask.capture_tasks_state,
                                   next_state=DeletingTask.confirmation_state,
                                   call_base=CALL_DELETE_TASK,
                                   menu_pack=menu_delete_task,
                                   is_only_one=True)
    await tasks_state.update_state_for_deleting_tasks()
    await state.update_data(capture_tasks_state=tasks_state)

    confirmation_state = InputStateParams(self_state = DeletingTask.confirmation_state,
                                          menu_pack= menu_delete_task,
                                          call_base=CALL_DELETE_TASK,
                                          is_last_state_with_changing_mode=True)
    await confirmation_state.update_state_for_delete_confirmation_state()
    await state.update_data(confirmation_state=confirmation_state)

    first_state = users_state

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

@deleting_task_router.message(F.text, DeletingTask.capture_tasks_state)
@deleting_task_router.message(F.text, DeletingTask.capture_users_state)
async def admin_deleting_capture(message: Message, state: FSMContext):
    # проверяем слово в базе данных
    # создаем экземпляр класса для обработки текущего состояния фсм
    current_fsm = FSMExecutor()
    # обрабатываем экземпляра класса, который анализирует наш колл и выдает сообщение и клавиатуру
    await current_fsm.execute(fsm_state=state, fsm_mess=message)
    state_text = await state_text_builder(state)
    message_text = state_text + '\n' + current_fsm.message_text
    await message_answer(source=message, message_text=message_text, reply_markup=current_fsm.reply_kb)


@deleting_task_router.callback_query(F.data.startswith(CALL_DELETE_TASK), DeletingTask.capture_tasks_state)
@deleting_task_router.callback_query(F.data.startswith(CALL_DELETE_TASK), DeletingTask.capture_users_state)
async def set_scheme_capture_words_from_call(call: CallbackQuery, state: FSMContext):
    fsm_state_str_curr = await state.get_state()
    # создаем экземпляр класса для обработки текущего состояния фсм
    current_fsm = FSMExecutor()
    # обрабатываем экземпляра класса, который анализирует наш колл и выдает сообщение и клавиатуру
    await current_fsm.execute(fsm_state=state, fsm_call=call)
    # отвечаем заменой сообщения
    fsm_state_str_next = await state.get_state()
    reply_kb= current_fsm.reply_kb
    state_text = await state_text_builder(state)
    message_text = state_text + '\n' + current_fsm.message_text

    if fsm_state_str_curr == DeletingTask.capture_users_state.state:
        users_state: InputStateParams = await state.get_value('capture_users_state')
        current_user_id = users_state.set_of_items
        user_id = next(iter(current_user_id))
        tasks_state: InputStateParams = await state.get_value('capture_tasks_state')
        await tasks_state.update_state_for_deleting_tasks(user_id=user_id)

        if len(tasks_state.buttons_pack) == 0:
            reply_kb = await keyboard_builder(menu_pack=menu_delete_task)
            message_text = MESS_NO_TASKS

        else:
            await state.update_data(capture_tasks_state=tasks_state)
            reply_kb = await keyboard_builder(menu_pack=tasks_state.menu_pack,
                                          buttons_pack=tasks_state.buttons_pack,
                                          buttons_base_call=tasks_state.call_base,
                                          buttons_cols=tasks_state.buttons_cols,
                                          buttons_rows=tasks_state.buttons_rows,
                                          is_adding_confirm_button=not tasks_state.is_only_one)

    await call.message.edit_text(message_text, reply_markup=reply_kb)
    await call.answer()


# конечный обработчик всего стейта
@deleting_task_router.callback_query(F.data.startswith(CALL_DELETE_TASK), DeletingTask.confirmation_state)
async def admin_deleting_task_capture_confirmation_from_call(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека уровень
    confirm = call.data
    confirm = confirm.replace(CALL_DELETE_TASK, '')

    if confirm == CALL_CONFIRM:

        capture_users: InputStateParams = await state.get_value('capture_users_state')
        users_set = capture_users.set_of_items

        capture_tasks: InputStateParams = await state.get_value('capture_tasks_state')
        tasks_set = capture_tasks.set_of_items

        state_text = await state_text_builder(state)

        res = True

        for task_id in tasks_set:
            res = res and await delete_task_from_db(task_id=task_id)

        message_text = f'----- ----- -----\n{state_text}----- ----- -----\n'

        if res:
            message_text += MESS_ADDED_TO_DB
        else:
            message_text += MESS_ERROR_ADDED_TO_DB

        reply_kb = await keyboard_builder(menu_pack=menu_delete_task, buttons_base_call="")

        await call.message.edit_text(message_text, reply_markup=reply_kb)
        await call.answer()

