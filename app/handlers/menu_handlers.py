from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import  CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
# my imports
from config import ADMIN_IDS
from app.database.models import Task
from app.database.requests import set_user, get_tasks
from app.handlers.states.menu_state_params import MenuStateParams
from app.admin_utils import message_answer
from app.keyboards.keyboard_builder import keyboard_builder, update_button_with_tasks_num
from app.keyboards.menu_buttons import *
# routers
from app.handlers.admin_menu.admin_setting.setting_scheme_handlers import setting_scheme_router
from app.handlers.admin_menu.admin_setting.setting_colls_handlers import setting_colls_router
from app.handlers.admin_menu.admin_adding.adding_source_handlers import adding_source_router
from app.handlers.admin_menu.admin_adding.adding_word_handlers import adding_word_router
from app.handlers.admin_menu.admin_adding.adding_coll_handlers import adding_coll_router
from app.handlers.admin_menu.admin_adding.adding_group_handlers import adding_group_router
from app.handlers.admin_menu.admin_adding.adding_homework_handlers import adding_homework_router
from app.handlers.admin_menu.admin_adding.adding_links_handlers import adding_link_router
from app.handlers.admin_menu.admin_deleting.deleting_task_handlers import deleting_task_router
from app.handlers.common_menu.links_handlers import links_router
from app.handlers.common_menu.tasks_handlers import tasks_router
from app.handlers.common_menu.revision_handlers import revision_router
from app.handlers.common_menu.homework_handlers import homework_router
from app.handlers.common_menu.config_handlers import config_router

menu_router = Router()
menu_router.include_router(adding_source_router)
menu_router.include_router(adding_word_router)
menu_router.include_router(adding_coll_router)
menu_router.include_router(adding_group_router)
menu_router.include_router(adding_homework_router)
menu_router.include_router(adding_link_router)
menu_router.include_router(setting_scheme_router)
menu_router.include_router(setting_colls_router)
menu_router.include_router(deleting_task_router)
menu_router.include_router(links_router)
menu_router.include_router(tasks_router)
menu_router.include_router(revision_router)
menu_router.include_router(homework_router)
menu_router.include_router(config_router)


class MenuState(StatesGroup):
    current_menu_params = State()

@menu_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext):
    print('0. добавь картинку в главное меню?')
    print('1. разнести настройки и токен в два разных файла')
    print('2. шедулер ревижн')
    print('3. мидлварь ревижн')
    print('4. объединение функций добавления элемента в множество, сейчас их 3')
    print('5. ревижн моделс и реквестс полный, разобраться в склалчеми')
    print('6. обработать ввод сообщения в процессе выполнения заданий')
    print('7. ревижн блокировка пользователя')
    print('8. сделать связь многие ко многим в линкс и юзерс')
    print('9. напиши хелп')
    print('10. разработай полностью новую систему тестов')
    print('10. разработай полностью новую систему тестов')
    print('11. список юзеров в таблице группы может быть пустым, поменять алембиком')
    print('12. revision logger')
    print('13. config можно оставить пустые напоминалки')
    print('14. сделать статистику')
    # чистим стейт
    await state.clear()
    # проверяем пользователя и регистрируем при необходимости
    await set_user(message)
    main_menu_params = MenuStateParams(curr_call=CALL_MAIN_MENU,
                                       curr_menu=
                                       [
                                           [button_quick_menu],
                                           [button_revision_menu, button_links_menu],
                                           [button_homework_menu, button_config_menu]
                                       ],
                                       curr_main_mess=MESS_MAIN_MENU)
    if message.from_user.id in ADMIN_IDS:
        await main_menu_params.update_with_admin_menu()
    current_menu_params = main_menu_params
    tasks: list[Task] = await get_tasks(request_user_tg_id=message.from_user.id, for_quick_tasks_menu=True)
    if tasks:
        current_menu_params.curr_menu[0][0] = update_button_with_tasks_num(current_menu_params.curr_menu[0][0], len(tasks))

    await state.clear()
    await state.update_data(current_menu_params=current_menu_params)
    await state.set_state(MenuState.current_menu_params)

    await message_answer(source=message,
                         message_text=current_menu_params.curr_main_mess,
                         reply_markup=await keyboard_builder(menu_pack=current_menu_params.curr_menu,
                                                             buttons_base_call=""))


@menu_router.callback_query(F.data == CALL_ADMIN_MENU)
@menu_router.callback_query(F.data == CALL_ADDING_MENU)
@menu_router.callback_query(F.data == CALL_EDITING_MENU)
@menu_router.callback_query(F.data == CALL_DELETING_MENU)
@menu_router.callback_query(F.data == CALL_SETTING_MENU)
@menu_router.callback_query(F.data == CALL_REVISION_MENU)
@menu_router.callback_query(F.data == CALL_CONFIG_MENU)
@menu_router.callback_query(F.data == CALL_MAIN_MENU)
async def admin_menu_setting_button(call: CallbackQuery, state: FSMContext):

    if call.data == CALL_ADMIN_MENU and call.from_user.id in ADMIN_IDS:
        current_state_params = MenuStateParams(curr_call=CALL_ADMIN_MENU,
                                               curr_menu=
                                               [
                                                   [button_adding_menu],
                                                   [button_editing_menu],
                                                   [button_setting_menu],
                                                   [button_deleting_menu],
                                                   [button_main_menu_back]
                                               ],
                                               curr_main_mess=MESS_ADMIN_MENU)

    elif call.data == CALL_ADDING_MENU and call.from_user.id in ADMIN_IDS:
        current_state_params = MenuStateParams(curr_call=CALL_ADDING_MENU,
                                               curr_menu=[[button_add_source],
                                                          [button_add_word],
                                                          [button_add_coll],
                                                          [button_add_test],
                                                          [button_add_link],
                                                          [button_add_group],
                                                          [button_add_homework],
                                                          [button_admin_menu_back, button_main_menu_back]],
                                               curr_main_mess=MESS_ADDING_MENU)

    elif call.data == CALL_EDITING_MENU and call.from_user.id in ADMIN_IDS:
        current_state_params = MenuStateParams(curr_call=CALL_EDITING_MENU,
                                               curr_menu=
                                               [
                                                   [button_edit_source],
                                                   [button_edit_word],
                                                   [button_edit_coll],
                                                   [button_edit_link],
                                                   [button_edit_group],
                                                   [button_edit_homework],
                                                   [button_admin_menu_back, button_main_menu_back]
                                               ],
                                               curr_main_mess=MESS_EDITING_MENU)

    elif call.data == CALL_DELETING_MENU and call.from_user.id in ADMIN_IDS:
        current_state_params = MenuStateParams(curr_call=CALL_DELETING_MENU,
                                               curr_menu=
                                               [
                                                   [button_delete_task],
                                                   [button_admin_menu_back, button_main_menu_back]
                                               ],
                                               curr_main_mess=MESS_EDITING_MENU)

    elif call.data == CALL_SETTING_MENU and call.from_user.id in ADMIN_IDS:
        current_state_params = MenuStateParams(curr_call=CALL_SETTING_MENU,
                                               curr_menu=[[button_set_scheme],
                                                          [button_set_coll],
                                                          [button_admin_menu_back, button_main_menu_back]],
                                               curr_main_mess=MESS_SETTING_MENU)

    elif call.data == CALL_REVISION_MENU:
        current_state_params = MenuStateParams(curr_call=CALL_REVISION_MENU,
                                               curr_menu=[[button_revision_sources],
                                                          [button_revision_words_menu],
                                                          [button_revision_colls_menu],
                                                          [button_main_menu_back]],
                                               curr_main_mess=MESS_REVISION_MENU)

    elif call.data == CALL_CONFIG_MENU:
        current_state_params = MenuStateParams(curr_call=CALL_CONFIG_MENU,
                                               curr_menu=[[button_config_sending_time],
                                                          [button_main_menu_back]],
                                               curr_main_mess=MESS_CONFIG_MENU)

    else:
        main_menu_params = MenuStateParams(curr_call=CALL_MAIN_MENU,
                                           curr_menu=
                                           [
                                               [button_quick_menu],
                                               [button_revision_menu, button_links_menu],
                                               [button_homework_menu, button_config_menu]
                                           ],
                                           curr_main_mess=MESS_MAIN_MENU)
        if call.from_user.id in ADMIN_IDS:
            await main_menu_params.update_with_admin_menu()
        tasks: list[Task] = await get_tasks(request_user_tg_id=call.from_user.id, for_quick_tasks_menu=True)
        current_state_params = main_menu_params
        if tasks:
            current_state_params.curr_menu[0][0] = update_button_with_tasks_num(current_state_params.curr_menu[0][0],
                                                                                len(tasks))

    await state.clear()
    await state.update_data(current_menu_params=current_state_params)
    await state.set_state(MenuState.current_menu_params)

    await message_answer(source=call,
                         message_text=current_state_params.curr_main_mess,
                         reply_markup=await keyboard_builder(menu_pack=current_state_params.curr_menu,
                                                             buttons_base_call=""))
    await call.answer()


@menu_router.message(F.text, MenuState.current_menu_params)
async def admin_menu_setting_button(message: Message, state: FSMContext):

    current_state_params: MenuStateParams = await state.get_value('current_menu_params')
    message_text = f'{message.text}?\n{current_state_params.curr_main_mess}'
    reply_kb = await keyboard_builder(menu_pack=current_state_params.curr_menu, buttons_base_call="")
    await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
