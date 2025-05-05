from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.keyboards.menu_buttons import *
from app.common_settings import *
from app.database.requests import get_links_by_filters, get_users_by_filters
from app.utils.admin_utils import get_new_page_num
from app.keyboards.keyboard_builder import keyboard_builder

links_router = Router()

class LinksState(StatesGroup):
    links_state = State()

# переход в меню добавления задания по схеме
@links_router.callback_query(F.data.startswith(CALL_LINKS_MENU))
async def show_links(call: CallbackQuery, state: FSMContext):
    user_id = (await get_users_by_filters(user_tg_id=call.from_user.id)).id
    buttons_page = 0
    link_kb_buttons = []
    links = await get_links_by_filters(user_id=user_id)
    if links:
        call_item = call.data.replace(CALL_LINKS_MENU, '')
        for link in links:
            curr_button = InlineKeyboardButton(text=link.name, url=link.link)
            link_kb_buttons.append(curr_button)
        if call_item:
            buttons_page = get_new_page_num(call=call,
                                            button_list=link_kb_buttons,
                                            call_base=CALL_LINKS_MENU,
                                            cols=NUM_SHOW_LINKS_COLS,
                                            rows=NUM_SHOW_LINKS_ROWS)
        message_text = MESS_LINKS_MENU
    else:
        message_text = MESS_LINKS_MENU_EMPTY
    reply_kb = await keyboard_builder(menu_pack=[[button_main_menu_back]],
                                      buttons_pack=link_kb_buttons,
                                      buttons_base_call=CALL_LINKS_MENU,
                                      buttons_cols=NUM_SHOW_LINKS_COLS,
                                      buttons_rows=NUM_SHOW_LINKS_ROWS,
                                      is_adding_confirm_button=False,
                                      buttons_page_number=buttons_page)

    await call.message.edit_text(text=message_text, reply_markup=reply_kb)
    await call.answer()

