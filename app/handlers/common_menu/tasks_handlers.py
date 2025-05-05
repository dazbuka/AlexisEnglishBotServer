
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.keyboards.menu_buttons import *
from app.common_settings import *
from app.database.requests import get_tasks, get_users_by_filters,  update_task_status, \
    get_medias_by_filters, get_words_by_filters, set_task
from app.utils.admin_utils import mess_answer, message_answer
from app.keyboards.keyboard_builder import (keyboard_builder, update_button_with_call_item,
                                            update_button_with_call_base, update_button_with_tasks_num)
from aiogram.exceptions import TelegramBadRequest
from config import logger
from datetime import datetime, timedelta
from app.database.models import Media, Task

tasks_router = Router()

class TasksState(StatesGroup):
    tasks_state = State()

# переход в меню добавления задания по схеме
@tasks_router.callback_query(F.data.startswith(CALL_TASKS_MENU))
async def tasks_main(call: CallbackQuery, state: FSMContext):
    await state.set_state(TasksState.tasks_state)
    tasks : list[Task] = await get_tasks(user_tg_id=call.from_user.id, for_quick_tasks_menu=True)
    if tasks:
        curr_task = tasks[0]
        media_id = curr_task.media_id
        curr_media: Media = await get_medias_by_filters(media_id_new=media_id)
        if len(tasks) > 1:
            button_next_task_updated = update_button_with_call_base(button_next_task, CALL_TASKS_MENU)
            button_next_task_updated = update_button_with_tasks_num(button_next_task_updated, len(tasks) - 1)
            menu_quick_tasks = [
                                    [
                                        update_button_with_call_item(button_translation, str(curr_task.media.word_id)),
                                        update_button_with_call_item(button_definition, str(curr_task.media.word_id)),
                                        update_button_with_call_item(button_repeat_today, str(curr_task.media.id))
                                    ],
                                    [
                                        button_next_task_updated
                                    ],
                                    [
                                        button_main_menu_back
                                    ]
                                ]
        else:
            menu_quick_tasks = [
                [
                    update_button_with_call_item(button_translation, str(curr_media.word_id)),
                    update_button_with_call_item(button_definition, str(curr_media.word_id)),
                    update_button_with_call_item(button_repeat_today, str(curr_media.id))
                ],
                [
                    button_main_menu_back
                ]
            ]
        reply_kb = await keyboard_builder(menu_pack=menu_quick_tasks, buttons_base_call='')


        # формируем сообщение
        # коллокация
        message_text = f'Collocation: <b>{curr_task.media.collocation}</b>'
        # если есть кэпшн - добавляем
        if curr_task.media.caption:
            message_text += f'\n\n{curr_task.media.caption}'
        # формируем примечание
        add_text = f'- task for {curr_task.time.strftime('%d.%m.%Y')} - word: <b>{curr_task.media.word.word}</b> - '
        if curr_task.media.word.source_id:
            add_text += f'source: {curr_task.media.word.source.source_name} -'
        add_text = '<i>' + add_text + '</i>'
        # добавляем примечание
        message_text += f'\n\n{add_text}'

        await mess_answer(source=call,
                          media_type=curr_task.media.media_type,
                          media_id=curr_task.media.telegram_id,
                          message_text=message_text,
                          reply_markup=reply_kb)
        await update_task_status(tasks[0].id)
    else:
        menu_quick_tasks = [[button_main_menu_back]]
        reply_kb = await keyboard_builder(menu_pack=menu_quick_tasks, buttons_base_call='')
        await message_answer(source=call, message_text=MESS_USER_ALL_DONE, reply_markup=reply_kb)

    await call.answer()


# @tasks_router.message(F.text, TasksState.tasks_state)
# async def set_capture_from_message(message: Message, state: FSMContext):
#     pass

@tasks_router.callback_query(F.data.startswith(CALL_DEFINITION))
async def tasks_main2(call: CallbackQuery):
    word_id = int(call.data.replace(CALL_DEFINITION, ''))
    word = await get_words_by_filters(word_id_new=word_id)
    try:
        await call.answer(f'{word.word} - {word.definition}', show_alert=True)
    except TelegramBadRequest as e:
        logger.error(f'{call.from_user.username} ({call.from_user.first_name})'
                     f' - ошибка definition для {word.word} *{call.data}*: {e}')
        await call.answer(f"Can't show definition, because it is too long", show_alert=True)


@tasks_router.callback_query(F.data.startswith(CALL_TRANSLATION))
async def tasks_main2(call: CallbackQuery):
    word_id = int(call.data.replace(CALL_TRANSLATION, ''))
    word = await get_words_by_filters(word_id_new=word_id)
    try:
        await call.answer(f'{word.word} - {word.translation}', show_alert=True)
    except TelegramBadRequest as e:
        logger.error(f'{call.from_user.username} ({call.from_user.first_name})'
                     f' - ошибка translation для {word.word} *{call.data}*: {e}')
        await call.answer(f"Can't show definition, because it is too long", show_alert=True)


@tasks_router.callback_query(F.data.startswith(CALL_REPEAT))
async def repeat_today(call: CallbackQuery):
    # вытаскиваем из колбека номер коллокации и пользователя
    media_id=int(call.data.replace(CALL_REPEAT, ''))
    user = await get_users_by_filters(user_tg_id=call.from_user.id)
    # добавляем задание на сегодня
    await set_task(user_id=user.id, media_id=media_id, task_time=datetime.now()+timedelta(days=1), author_id=user.id)
    await call.answer('Task added')

