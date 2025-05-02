from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from config import logger
import app.database.requests as rq
import app.keyboards.user_keyboards as ukb
from app.utils.admin_utils import message_answer
import data.user_messages as umsg
import data.common_messages as cmsg

user_homework_router = Router()


# хендлер перехода в меню settings - пункт главного меню
@user_homework_router.callback_query(F.data == cmsg.COMMON_BUTTON_HOMEWORK)
async def show_homework(call : CallbackQuery, state: FSMContext):
    # сообщение логгеру
    logger.info(f'{call.from_user.username} ({call.from_user.first_name})'
                f' - показываю домашнее задание *{call.data}*')
    # очищаем стейт на всякий случай
    await state.clear()
    homeworks = await rq.get_homeworks_by_filters()

    if homeworks:
        user_im = await rq.get_users_by_filters(user_tg_id=call.from_user.id)
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
            message_text = f'{umsg.USER_YOUR_HOMEWORK}\n\n{text}\n\n{umsg.USER_INVITE_PRESS_ANY_BUTTON}'
        else:
            message_text = f'{umsg.USER_YOUR_NO_HOMEWORK}\n\n{umsg.USER_INVITE_PRESS_ANY_BUTTON}'
    else:
        message_text = f'{umsg.USER_YOUR_NO_HOMEWORK}\n\n{umsg.USER_INVITE_PRESS_ANY_BUTTON}'
    reply_kb = await ukb.common_main_kb(call.from_user.id)
    await message_answer(source=call, message_text=message_text, reply_markup=reply_kb)
    await call.answer()