# from asyncio import current_task
import re
from aiogram.fsm.context import FSMContext
from typing import List
from aiogram.fsm.state import State, StatesGroup
from app.database.models import Media, Task
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from app.keyboards.menu_buttons import *
from app.common_settings import *
from app.database.requests import get_tasks, get_medias_by_filters
from app.utils.admin_utils import mess_answer, message_answer
from app.keyboards.keyboard_builder import keyboard_builder

from app.handlers.admin_menu.states.state_params import InputStateParams
from app.handlers.admin_menu.states.state_executor import FSMExecutor

revision_router = Router()

menu_revision = [[button_revision_menu_back,
                  button_main_menu_back]]

class RevisionState(StatesGroup):
    revision_sources_state = State()
    revision_words_state = State()
    revision_colls_state = State()

@revision_router.callback_query(F.data == CALL_REVISION_SOURCES)
@revision_router.callback_query(F.data == CALL_REVISION_WORDS)
@revision_router.callback_query(F.data == CALL_REVISION_COLLS)
async def revision_start(call: CallbackQuery, state: FSMContext):
    tasks: List['Task'] = await get_tasks(user_tg_id=call.from_user.id, sent=True, media_task_only=True)
    user_colls = {task.media_id for task in tasks if task.media_id}
    user_words = {task.media.word_id for task in tasks if task.media.word_id}
    user_sources = {task.media.word.source_id for task in tasks if task.media.word.source_id}

    revision_sources_state = InputStateParams(self_state=RevisionState.revision_sources_state,
                                              next_state=RevisionState.revision_words_state,
                                              call_base=CALL_REVISION_SOURCES,
                                              menu_pack=menu_revision,
                                              is_only_one=True)
    await revision_sources_state.update_state_for_sources_revision(sources_set=user_sources)
    await state.update_data(revision_sources_state=revision_sources_state)

    revision_words_state = InputStateParams(self_state=RevisionState.revision_words_state,
                                            next_state=RevisionState.revision_colls_state,
                                            call_base=CALL_REVISION_WORDS,
                                            menu_pack=menu_revision,
                                            is_only_one=True)
    await revision_words_state.update_state_for_words_revision(words_set=user_words)
    await state.update_data(revision_words_state=revision_words_state)

    revision_colls_state = InputStateParams(self_state=RevisionState.revision_colls_state,
                                            next_state=RevisionState.revision_colls_state,
                                            call_base=CALL_REVISION_COLLS,
                                            menu_pack=menu_revision,
                                            is_only_one=True,
                                            is_media_revision_mode=True)
    await revision_colls_state.update_state_for_colls_revision(colls_set=user_colls)
    await state.update_data(revision_colls_state=revision_colls_state)

    if call.data == CALL_REVISION_SOURCES:
        first_state = revision_sources_state
    elif call.data == CALL_REVISION_WORDS:
        first_state = revision_words_state
    else: #if call.data == CALL_REVISION_COLLS:
        first_state = revision_colls_state

    message_text = first_state.main_mess
    await state.set_state(first_state.self_state)
    reply_kb = await keyboard_builder(menu_pack=first_state.menu_pack,
                                      buttons_pack=first_state.buttons_pack,
                                      buttons_base_call=first_state.call_base,
                                      buttons_cols=first_state.buttons_cols,
                                      buttons_rows=first_state.buttons_rows)

    await call.message.edit_text(text=message_text, reply_markup=reply_kb)
    await call.answer()

@revision_router.callback_query(F.data.startswith(CALL_REVISION_SOURCES), RevisionState.revision_sources_state)
@revision_router.callback_query(F.data.startswith(CALL_REVISION_WORDS), RevisionState.revision_words_state)
async def revision_sources_words_loop(call: CallbackQuery, state: FSMContext):
    # создаем экземпляр класса для обработки текущего состояния фсм
    fsm_state_str = await state.get_state()
    # проверяем слово в базе данных
    if fsm_state_str == RevisionState.revision_sources_state:
        revision_words_state: InputStateParams = await state.get_value('revision_words_state')
        call_item = call.data.replace(CALL_REVISION_SOURCES, '')
        if re.match(r'^\d+$', call_item):
            await revision_words_state.update_state_for_words_revision(source_id=int(call_item))
            await state.update_data(revision_words_state=revision_words_state)


    if fsm_state_str == RevisionState.revision_words_state:
        revision_colls_state: InputStateParams = await state.get_value('revision_colls_state')
        call_item = call.data.replace(CALL_REVISION_WORDS, '')
        if re.match(r'^\d+$', call_item):
            await revision_colls_state.update_state_for_colls_revision(word_id=int(call_item))
            await state.update_data(revision_colls_state=revision_colls_state)


    current_fsm = FSMExecutor()
    # обрабатываем экземпляра класса, который анализирует наш колл и выдает сообщение и клавиатуру
    await current_fsm.execute(fsm_state=state, fsm_call=call)
    # отвечаем заменой сообщения
    await call.message.edit_text(text=current_fsm.message_text, reply_markup=current_fsm.reply_kb)
    await call.answer()



@revision_router.callback_query(F.data.startswith(CALL_REVISION_COLLS), RevisionState.revision_colls_state)
async def revision_collocations_loop(call: CallbackQuery, state: FSMContext):
    # создаем экземпляр класса для обработки текущего состояния фсм
    current_fsm = FSMExecutor()
    # обрабатываем экземпляра класса, который анализирует наш колл и выдает сообщение и клавиатуру
    await current_fsm.execute(fsm_state=state, fsm_call=call)
    next_state_str = await state.get_state()
    next_state = next_state_str.split(':', 1)[1]
    next_state_params: InputStateParams = await state.get_value(next_state)
    if next_state_params.set_of_items:
        media_id = list(next_state_params.set_of_items)[0]
        media: Media = await get_medias_by_filters(media_id_new=media_id)
        await mess_answer(source=call,
                          media_type=media.media_type,
                          media_id=media.telegram_id,
                          message_text=f'{media.collocation}\n\n{media.caption}',
                          reply_markup=current_fsm.reply_kb)
    # это для случая когда сразу нажимают карусельку
    else:
        await call.message.edit_text(text=current_fsm.message_text, reply_markup=current_fsm.reply_kb)
    await call.answer()

@revision_router.message(F.text, RevisionState.revision_sources_state)
@revision_router.message(F.text, RevisionState.revision_words_state)
@revision_router.message(F.text, RevisionState.revision_colls_state)
async def set_capture_from_message(message: Message, state: FSMContext):
    current_fsm = FSMExecutor()
    await current_fsm.execute(fsm_state=state, fsm_mess=message)
    await message_answer(source=message, message_text=current_fsm.message_text, reply_markup=current_fsm.reply_kb)