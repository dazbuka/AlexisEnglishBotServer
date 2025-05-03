import os
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from datetime import datetime
from app.database.models import Media, Source, Task, Word, Group
from app.keyboards.menu_buttons import *
from app.handlers.common_settings import *

from app.database.requests import get_users_by_filters, add_media_to_db, get_medias_by_filters, update_media_changing
from app.utils.admin_utils import (state_text_builder, mess_answer,
                                   get_shema_text_by_word_id)
from config import bot, media_dir

from app.handlers.admin_menu.states.state_executor import FSMExecutor
from app.handlers.admin_menu.states.state_params import (InputStateParams)
from app.keyboards.keyboard_builder import keyboard_builder, update_button_with_call_base

adding_coll_router = Router()

class AddColl(StatesGroup):
    author_id = State()
    capture_words_state = State()
    input_coll_state = State()
    capture_coll_changing = State()
    input_media_state = State()
    input_caption_state = State()
    capture_levels_state = State()
    capture_days_state = State()
    confirmation_state = State()


menu_add_coll = [
    [button_adding_menu_back, button_editing_menu_back, button_admin_menu, button_main_menu_back]
]

menu_add_coll_with_changing = [
    [update_button_with_call_base(button_change_words, CALL_ADD_COLL),
     update_button_with_call_base(button_change_collocation, CALL_ADD_COLL),
     update_button_with_call_base(button_change_levels, CALL_ADD_COLL)],
    [update_button_with_call_base(button_change_media, CALL_ADD_COLL),
     update_button_with_call_base(button_change_caption, CALL_ADD_COLL),
     update_button_with_call_base(button_change_days, CALL_ADD_COLL)],
    [button_setting_menu_back, button_admin_menu, button_main_menu_back]
]

# переход в меню добавления задания по схеме
@adding_coll_router.callback_query(F.data == CALL_EDIT_COLL)
@adding_coll_router.callback_query(F.data == CALL_ADD_COLL)
async def adding_word_first_state(call: CallbackQuery, state: FSMContext):
    # очистка стейта
    await state.clear()

    # задаем в стейт ид автора
    author = await get_users_by_filters(user_tg_id=call.from_user.id)
    await state.update_data(author_id=author.id)

    words_state = InputStateParams(self_state=AddColl.capture_words_state,
                                          next_state=AddColl.input_coll_state,
                                          call_base=CALL_ADD_COLL,
                                          menu_pack=menu_add_coll,
                                          is_only_one=True)
    await words_state.update_state_for_words_capture(words_filter='all')
    await state.update_data(capture_words_state=words_state)


    input_coll_text_state = InputStateParams(self_state = AddColl.input_coll_state,
                                             next_state = AddColl.input_media_state,
                                             call_base= CALL_ADD_COLL,
                                             main_mess= MESS_INPUT_COLL,
                                             menu_pack= menu_add_coll,
                                             is_input=True,
                                             is_only_one=True)
    await state.update_data(input_coll_state=input_coll_text_state)


    input_media_state = InputStateParams(self_state=AddColl.input_media_state,
                                         next_state=AddColl.capture_levels_state,
                                         call_base=CALL_ADD_COLL,
                                         main_mess=MESS_INPUT_MEDIA,
                                         menu_pack=menu_add_coll,
                                         is_input=True,
                                         is_only_one=True)
    await state.update_data(input_media_state=input_media_state)

    input_caption_text_state = InputStateParams(self_state=AddColl.input_caption_state,
                                                next_state=AddColl.confirmation_state,
                                                call_base=CALL_ADD_COLL,
                                                main_mess=MESS_INPUT_CAPTION,
                                                menu_pack=menu_add_coll,
                                                is_input=True,
                                                is_only_one=True)
    await state.update_data(input_caption_state=input_caption_text_state)


    levels_state = InputStateParams(self_state=AddColl.capture_levels_state,
                                            next_state=AddColl.capture_days_state,
                                            call_base=CALL_ADD_COLL,
                                            menu_pack=menu_add_coll,
                                            is_only_one=True)
    await levels_state.update_state_for_level_capture()
    await state.update_data(capture_levels_state=levels_state)


    days_state = InputStateParams(self_state=AddColl.capture_days_state,
                                        next_state=AddColl.confirmation_state,
                                        call_base=CALL_ADD_COLL,
                                        menu_pack=menu_add_coll,
                                        is_only_one=True)
    await days_state.update_state_for_days_capture()
    await state.update_data(capture_days_state=days_state)


    confirmation_state = InputStateParams(self_state = AddColl.confirmation_state,
                                                 call_base = CALL_ADD_COLL,
                                                 menu_pack= menu_add_coll_with_changing,
                                                 is_last_state_with_changing_mode=True)
    await confirmation_state.update_state_for_confirmation_state()
    await state.update_data(confirmation_state=confirmation_state)

    if call.data == CALL_EDIT_COLL:
        capture_coll_changing = InputStateParams(
            self_state=AddColl.capture_coll_changing,
            next_state=AddColl.confirmation_state,
            call_base=CALL_EDIT_COLL,
            menu_pack=menu_add_coll,
            is_only_one=True)
        await capture_coll_changing.update_state_for_colls_capture()
        await state.update_data(capture_coll_changing=capture_coll_changing)
        first_state = capture_coll_changing
    else:
        first_state = words_state



    # переход в первый стейт
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


@adding_coll_router.message(F.text, AddColl.capture_coll_changing)
@adding_coll_router.message(F.text, AddColl.capture_words_state)
@adding_coll_router.message(F.text, AddColl.input_coll_state)
@adding_coll_router.message(F.photo | F.video | F.text, AddColl.input_media_state)
@adding_coll_router.message(F.text, AddColl.input_caption_state)
@adding_coll_router.message(F.text, AddColl.capture_levels_state)
@adding_coll_router.message(F.text, AddColl.capture_days_state)
async def admin_adding_word_capture_word(message: Message, state: FSMContext):
    fsm_state_str = await state.get_state()
    # проверяем слово в базе данных
    # создаем экземпляр класса для обработки текущего состояния фсм
    current_fsm = FSMExecutor()
    # обрабатываем экземпляра класса, который анализирует наш колл и выдает сообщение и клавиатуру
    await current_fsm.execute(fsm_state=state, fsm_mess=message)

    # взимообмен кэпшен стейт и медиа стейт, в котором есть переменная кэпшн


    media_state: InputStateParams = await state.get_value('input_media_state')

    if fsm_state_str == AddColl.input_media_state.state:
        caption = media_state.input_text
        input_caption_state: InputStateParams = await state.get_value('input_caption_state')
        input_caption_state.input_text = caption
        await state.update_data(input_caption_state=input_caption_state)

    state_text = await state_text_builder(state)
    message_text = state_text + '\n' + current_fsm.message_text
    await mess_answer(source=message,
                      media_type=media_state.media_type,
                      media_id=media_state.media_id,
                      message_text=message_text,
                      reply_markup=current_fsm.reply_kb)


@adding_coll_router.callback_query(F.data.startswith(CALL_EDIT_COLL), AddColl.capture_coll_changing)
@adding_coll_router.callback_query(F.data.startswith(CALL_ADD_COLL), AddColl.capture_words_state)
@adding_coll_router.callback_query(F.data.startswith(CALL_ADD_COLL), AddColl.capture_levels_state)
@adding_coll_router.callback_query(F.data.startswith(CALL_ADD_COLL), AddColl.capture_days_state)
async def set_scheme_capture_words_from_call(call: CallbackQuery, state: FSMContext):
    fsm_state_str_curr = await state.get_state()
    # создаем экземпляр класса для обработки текущего состояния фсм
    current_fsm = FSMExecutor()
    # обрабатываем экземпляра класса, который анализирует наш колл и выдает сообщение и клавиатуру
    await current_fsm.execute(fsm_state=state, fsm_call=call)
    # отвечаем заменой сообщения

    fsm_state_str_next = await state.get_state()

    if (fsm_state_str_curr == AddColl.capture_coll_changing.state and
            fsm_state_str_next == AddColl.confirmation_state.state):
        capture_coll_changing: InputStateParams = await state.get_value('capture_coll_changing')
        coll_id = int(list(capture_coll_changing.set_of_items)[0])
        coll: Media = await get_medias_by_filters(media_id_new=coll_id)

        await state.update_data(author_id=coll.author_id)

        capture_words_state: InputStateParams = await state.get_value('capture_words_state')
        capture_words_state.set_of_items = {coll.word_id}
        await state.update_data(capture_words_state=capture_words_state)

        input_coll_state: InputStateParams = await state.get_value('input_coll_state')
        input_coll_state.input_text = coll.collocation
        await state.update_data(input_coll_state=input_coll_state)

        input_media_state: InputStateParams = await state.get_value('input_media_state')
        input_media_state.media_id = coll.telegram_id
        input_media_state.media_type = coll.media_type
        input_media_state.input_text = coll.caption
        await state.update_data(input_media_state=input_media_state)

        input_caption_state: InputStateParams = await state.get_value('input_caption_state')
        input_caption_state.input_text = coll.caption
        await state.update_data(input_caption_state=input_caption_state)

        levels_state: InputStateParams = await state.get_value('capture_levels_state')
        levels_state.set_of_items = {coll.level}
        await state.update_data(capture_levels_state=levels_state)

        capture_days_state: InputStateParams = await state.get_value('capture_days_state')
        capture_days_state.set_of_items = {coll.study_day}
        await state.update_data(capture_days_state=capture_days_state)

        confirmation_state: InputStateParams = await state.get_value('confirmation_state')
        confirmation_state.call_base = CALL_EDIT_COLL
        # confirmation_state.main_mess = MESS_ADD_ENDING
        await state.update_data(confirmation_state=confirmation_state)

    media_state: InputStateParams = await state.get_value('input_media_state')

    state_text = await state_text_builder(state)
    message_text = state_text + '\n' + current_fsm.message_text

    if fsm_state_str_next == AddColl.capture_days_state.state:
        word_state: InputStateParams = await state.get_value('capture_words_state')
        word_id = list(word_state.set_of_items)[0]
        scheme = await get_shema_text_by_word_id(word_id=word_id)
        message_text += '\n\n' + scheme

    await mess_answer(source=call,
                      media_type=media_state.media_type,
                      media_id=media_state.media_id,
                      message_text=message_text,
                      reply_markup=current_fsm.reply_kb)
    await call.answer()


# конечный обработчик всего стейта
@adding_coll_router.callback_query(F.data.startswith(CALL_EDIT_COLL), AddColl.confirmation_state)
@adding_coll_router.callback_query(F.data.startswith(CALL_ADD_COLL), AddColl.confirmation_state)
async def admin_adding_task_capture_confirmation_from_call(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека уровень
    confirm = call.data
    if call.data.startswith(CALL_ADD_COLL):
        confirm = confirm.replace(CALL_ADD_COLL, '')
    if call.data.startswith(CALL_EDIT_COLL):
        confirm = confirm.replace(CALL_EDIT_COLL, '')


    if (confirm == CALL_CHANGING_WORDS or confirm == CALL_CHANGING_COLL or confirm == CALL_CHANGING_LEVELS
            or confirm == CALL_CHANGING_CAPTION or confirm == CALL_CHANGING_MEDIA or confirm == CALL_CHANGING_DAYS):

        confirmation_state: InputStateParams = await state.get_value('confirmation_state')

        if confirm == CALL_CHANGING_WORDS:
            # при нажатии на изменение задаем следующий стейт элементов
            confirmation_state.next_state = AddColl.capture_words_state
            # делаем так, чтобы в стейте добавления последний стейт (на изменения который) стал следующим
            capture_words_state: InputStateParams = await state.get_value('capture_words_state')
            capture_words_state.next_state = AddColl.confirmation_state
            await state.update_data(capture_words_state=capture_words_state)

        elif confirm == CALL_CHANGING_COLL:
            # при нажатии на изменение задаем следующий стейт элементов
            confirmation_state.next_state = AddColl.input_coll_state
            # делаем так, чтобы в стейте добавления последний стейт (на изменения который) стал следующим
            input_coll_state: InputStateParams = await state.get_value('input_coll_state')
            input_coll_state.next_state = AddColl.confirmation_state
            await state.update_data(input_coll_state=input_coll_state)

        elif confirm == CALL_CHANGING_LEVELS:
            # при нажатии на изменение задаем следующий стейт элементов
            confirmation_state.next_state = AddColl.capture_levels_state
            # делаем так, чтобы в стейте добавления последний стейт (на изменения который) стал следующим
            capture_levels_state: InputStateParams = await state.get_value('capture_levels_state')
            capture_levels_state.next_state = AddColl.confirmation_state
            await state.update_data(capture_levels_state=capture_levels_state)

        elif confirm == CALL_CHANGING_MEDIA:
            # при нажатии на изменение задаем следующий стейт элементов
            confirmation_state.next_state = AddColl.input_media_state
            # делаем так, чтобы в стейте добавления последний стейт (на изменения который) стал следующим
            input_media_state: InputStateParams = await state.get_value('input_media_state')
            input_media_state.next_state = AddColl.confirmation_state
            await state.update_data(input_media_state=input_media_state)

        elif confirm == CALL_CHANGING_CAPTION:
            # при нажатии на изменение задаем следующий стейт элементов
            confirmation_state.next_state = AddColl.input_caption_state
            # делаем так, чтобы в стейте добавления последний стейт (на изменения который) стал следующим
            input_caption_state: InputStateParams = await state.get_value('input_caption_state')
            input_caption_state.next_state = AddColl.confirmation_state
            await state.update_data(input_caption_state=input_caption_state)

        elif confirm == CALL_CHANGING_DAYS:
            # при нажатии на изменение задаем следующий стейт элементов
            confirmation_state.next_state = AddColl.capture_days_state
            # делаем так, чтобы в стейте добавления последний стейт (на изменения который) стал следующим
            capture_days_state: InputStateParams = await state.get_value('capture_days_state')
            capture_days_state.next_state = AddColl.confirmation_state
            await state.update_data(capture_days_state=capture_days_state)

        await state.update_data(confirmation_state=confirmation_state)
        current_fsm = FSMExecutor()
        await current_fsm.execute(state, call)

        media_state: InputStateParams = await state.get_value('input_media_state')

        state_text = await state_text_builder(state)
        message_text = state_text + '\n' + current_fsm.message_text

        await mess_answer(source=call,
                          media_type=media_state.media_type,
                          media_id=media_state.media_id,
                          message_text=message_text,
                          reply_markup=current_fsm.reply_kb)
        await call.answer()


    elif confirm == CALL_CONFIRM:
        # основной обработчик, запись в бд
        author_id = await state.get_value('author_id')

        capture_words: InputStateParams = await state.get_value('capture_words_state')
        words_set = capture_words.set_of_items

        input_coll: InputStateParams = await state.get_value('input_coll_state')
        collocation = input_coll.input_text

        input_media: InputStateParams = await state.get_value('input_media_state')
        media_type = input_media.media_type
        media_tg_id = input_media.media_id
        input_caption: InputStateParams = await state.get_value('input_caption_state')
        caption = input_caption.input_text

        capture_levels: InputStateParams = await state.get_value('capture_levels_state')
        levels_set = capture_levels.set_of_items

        capture_days: InputStateParams = await state.get_value('capture_days_state')
        days_set = capture_days.set_of_items

        state_text = await state_text_builder(state)

        res = True
        for word_id in words_set:
            for level in levels_set:
                for study_day in days_set:
                    if call.data.startswith(CALL_ADD_COLL):
                        res = res and await add_media_to_db(media_type=media_type,
                                                            word_id=word_id,
                                                            collocation=collocation,
                                                            caption=caption,
                                                            telegram_id=media_tg_id,
                                                            study_day=study_day,
                                                            author_id=author_id,
                                                            level=level)

                    if call.data.startswith(CALL_EDIT_COLL):
                        capture_coll_changing: InputStateParams = await state.get_value('capture_coll_changing')
                        coll_id = int(list(capture_coll_changing.set_of_items)[0])
                        res = res and await update_media_changing(media_id=coll_id,
                                                                  media_type=media_type,
                                                                  word_id=word_id,
                                                                  collocation=collocation,
                                                                  caption=caption,
                                                                  telegram_id=media_tg_id,
                                                                  study_day=study_day,
                                                                  author_id=author_id,
                                                                  level=level)

        message_text = f'----- ----- -----\n{state_text}----- ----- -----\n'
        if res:
            message_text += MESS_ADDED_TO_DB
            if media_tg_id:
            # Получаем media_id
                media_id = (await get_medias_by_filters(telegram_id=media_tg_id))[0].id
                # Выделяем файл, который хотим сохранить
                file = await bot.get_file(media_tg_id)
                # Подпапка для сохранения
                path_name = datetime.now().strftime('%y-%m')
                # Проверяем наличие директории и создаем её, если её ещё нет

                if not os.path.exists(os.path.join(media_dir, path_name)):
                    os.makedirs(os.path.join(media_dir, path_name))
                   # Даем название и путь этому файлу
                for word in words_set:
                    filename = f"{media_id}-{media_type}-{word}{os.path.splitext(file.file_path)[1]}"
                    dest_path = os.path.join(media_dir, path_name, filename)
                    # Скачиваем файл
                    await bot.download_file(file.file_path, dest_path)
        else:
            message_text += MESS_ERROR_ADDED_TO_DB

        reply_kb = await keyboard_builder(menu_pack=menu_add_coll, buttons_base_call="")


        media_state: InputStateParams = await state.get_value('input_media_state')

        await mess_answer(source=call,
                          media_type=media_state.media_type,
                          media_id=media_state.media_id,
                          message_text=message_text,
                          reply_markup=reply_kb)
        await call.answer()

