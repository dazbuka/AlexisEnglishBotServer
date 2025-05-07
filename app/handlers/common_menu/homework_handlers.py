from aiogram import F, Router
from aiogram.types import CallbackQuery
from app.database.requests import get_homeworks_by_filters, get_users_by_filters
from app.admin_utils import message_answer
from app.common_settings import MESS_YOUR_HOMEWORK, MESS_YOUR_HOMEWORK_EMPTY
from app.keyboards.menu_buttons import button_main_menu_back
from app.common_settings import CALL_SHOW_HOMEWORK
from app.keyboards.keyboard_builder import keyboard_builder

homework_router = Router()

menu_show_homework = [[button_main_menu_back]]

# хендлер перехода в меню settings - пункт главного меню
@homework_router.callback_query(F.data == CALL_SHOW_HOMEWORK)
async def show_homework(call : CallbackQuery):
    homeworks = await get_homeworks_by_filters()
    if homeworks:
        user_im = await get_users_by_filters(user_tg_id=call.from_user.id)
        tasks = []
        for homework in homeworks:
            user_list = homework.users.replace(' ', '').split(',')
            for user_id in user_list:
                if user_im.id==int(user_id):
                    date = homework.time.strftime('%d.%m.%Y')
                    item = f'{date} - \n{homework.hometask}'
                    tasks.append(item)
        if tasks:
            text = '\n'.join(map(str,tasks))
            message_text = f'{MESS_YOUR_HOMEWORK}\n\n{text}'
        else:
            message_text = f'{MESS_YOUR_HOMEWORK_EMPTY}'
    else:
        message_text = f'{MESS_YOUR_HOMEWORK_EMPTY}'

    reply_kb = await keyboard_builder(menu_pack=menu_show_homework, buttons_base_call="")
    await message_answer(source=call, message_text=message_text, reply_markup=reply_kb)
    await call.answer()