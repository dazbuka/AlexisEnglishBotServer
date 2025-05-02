import os
from config import bot, STUDYING_DAY_LIST, media_dir
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery,ContentType
from datetime import datetime

import app.keyboards.admin_keyboards as akb
import app.database.requests as rq
import data.admin_messages as amsg
import data.common_messages as cmsg
import app.handlers.callback_messages as callmsg

from app.utils.admin_utils import (message_answer,
                                   send_any_media_to_user_with_kb,
                                   get_text_from_media_adding_state,
                                   get_word_list_for_kb_with_ids,
                                   get_shema_text_by_word_id)


admin_adding_media_router = Router()


class AddMedia(StatesGroup):
    author = State()
    word = State()
    word_id = State()
    level = State()
    collocation = State()
    telegram_id = State()
    media_type = State()
    caption = State()
    study_day = State()
    confirmation = State()


# хендлер начала ввода медиа, все начинается с выбора слова
@admin_adding_media_router.callback_query(F.data == amsg.ADMIN_BUTTON_ADD_MEDIA)
async def admin_adding_media_start(call: CallbackQuery, state: FSMContext):
    await state.clear()
    # получаем список слов, сразу заполняем id автора
    word_list = await get_word_list_for_kb_with_ids()
    reply_kb = await akb.admin_adding_media_kb(adding_word_list=word_list)
    user = await rq.get_users_by_filters(user_tg_id=call.from_user.id)
    await state.update_data(author=user.id)
    await call.message.edit_text(amsg.ADM_ADD_MEDIA_WORD, reply_markup=reply_kb)
    await call.answer()
    await state.set_state(AddMedia.word)


# хендлер захвата слова из клавиатуры (кнопок)
@admin_adding_media_router.callback_query(F.data.startswith(callmsg.CALL_ADM_ADD_MEDIA_WORD), AddMedia.word)
async def admin_adding_media_capture_word_from_call(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека слово и из базы данных забираем ид выбранного слова
    word_call=call.data.replace(callmsg.CALL_ADM_ADD_MEDIA_WORD, '')
    word_id = int(word_call.split('-', 1)[0])
    words = await rq.get_words_by_filters(word_id=word_id)
    await state.update_data(word=words[0].word)
    await state.update_data(word_id=words[0].id)
    # вытаскиваем из стейта текст сообщения
    state_text = await get_text_from_media_adding_state(state)
    message_text = f'{state_text}\n{amsg.ADM_ADD_MEDIA_COLLOCATION}'
    reply_kb = await akb.admin_adding_media_kb()
    await call.message.edit_text(message_text, reply_markup=reply_kb)
    await call.answer()
    await state.set_state(AddMedia.collocation)


# хендлер захвата слова из текста
@admin_adding_media_router.message(F.text, AddMedia.word)
async def admin_adding_media_capture_word_from_message(message: Message, state: FSMContext):
    # ищем напечатанное слово в базе данных
    words = await rq.get_words_by_filters(word=message.text.lower())
    # если найдены и объект один, обновляем стейт
    if words:
        if len(words)==1:
            await state.update_data(word=words[0].word)
            await state.update_data(word_id=words[0].id)
            state_text = await get_text_from_media_adding_state(state)
            message_text = f'{state_text}\n{amsg.ADM_ADD_MEDIA_COLLOCATION}'
            reply_kb = await akb.admin_adding_media_kb()
            await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
            await state.set_state(AddMedia.collocation)
    # если не найдены, ищем по кусочкам и выводим найденное
    else:
        words = await rq.get_words_by_filters(piece_of_word=message.text.lower())
        word_list = await get_word_list_for_kb_with_ids(words) if words else []
        message_text = amsg.ADM_ADD_MEDIA_WORD_NOT_FIND
        reply_kb = await akb.admin_adding_media_kb(adding_word_list=word_list)
        await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
        await state.set_state(AddMedia.word)


# хендлер приема коллокации
@admin_adding_media_router.message(F.text, AddMedia.collocation)
async def admin_adding_media_capture_collocation(message: Message, state: FSMContext):
    # обновляем стейт
    await state.update_data(collocation=message.text.lower().strip())
    state_text = await get_text_from_media_adding_state(state)
    message_text = f'{state_text}\n{amsg.ADM_ADD_MEDIA_LEVEL}'
    reply_kb = await akb.admin_adding_media_kb(adding_level=True)
    await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
    await state.set_state(AddMedia.level)


# хендлер приема колл уровня изучения
@admin_adding_media_router.callback_query(F.data.startswith(callmsg.CALL_ADM_ADD_MEDIA_LEVEL), AddMedia.level)
async def admin_adding_media_capture_level_from_call(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека уровень
    level=call.data.replace(callmsg.CALL_ADM_ADD_MEDIA_LEVEL, '')
    await state.update_data(level=level)
    state_text = await get_text_from_media_adding_state(state)
    message_text = f'{state_text}\n{amsg.ADM_ADD_MEDIA_MEDIA}'
    reply_kb = await akb.admin_adding_media_kb()
    await call.message.edit_text(message_text, reply_markup=reply_kb)
    await call.answer()
    await state.set_state(AddMedia.media_type)


# хендлер приема уровня изучения с текста - не пропускает дальше
@admin_adding_media_router.message(F.text, AddMedia.level)
async def admin_adding_media_capture_level_from_text(message: Message, state: FSMContext):
    state_text = await get_text_from_media_adding_state(state)
    message_text = f'{state_text}\n{amsg.ADM_ADD_MEDIA_INV_KB}'
    reply_kb = await akb.admin_adding_media_kb(adding_level=True)
    await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
    await state.set_state(AddMedia.level)


# хендлер приема медиа
@admin_adding_media_router.message(F.photo | F.video | F.text, AddMedia.media_type)
async def admin_adding_media_capture_media(message: Message, state: FSMContext):

    if message.content_type == ContentType.TEXT:
        await state.update_data(media_type='text')
        await state.update_data(caption=message.text)
    elif message.content_type == ContentType.PHOTO:
        await state.update_data(media_type='photo')
        await state.update_data(telegram_id=message.photo[-1].file_id)
        await state.update_data(caption=message.caption)
    elif message.content_type == ContentType.VIDEO:
        await state.update_data(media_type='video')
        await state.update_data(caption=message.caption)
        await state.update_data(telegram_id=message.video.file_id)

    schema = await get_shema_text_by_word_id((await state.get_data()).get("word_id"))
    state_text = await get_text_from_media_adding_state(state)
    message_text = f'{state_text}\n{amsg.ADM_ADD_MEDIA_DAY}\n{schema}'
    reply_kb = await akb.admin_adding_media_kb(adding_study_day=STUDYING_DAY_LIST)
    await send_any_media_to_user_with_kb(bot=bot,
                                         user_tg_id=message.from_user.id,
                                         media_type=(await state.get_data()).get("media_type"),
                                         caption=message_text,
                                         file_id=(await state.get_data()).get("telegram_id"),
                                         reply_kb=reply_kb)
    await state.set_state(AddMedia.study_day)


# хендлер приема дня изучения с текста
@admin_adding_media_router.message(F.text, AddMedia.study_day)
async def admin_adding_media_capture_study_day_from_message(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(study_day=int(message.text))
        state_text = await get_text_from_media_adding_state(state)
        message_text = f'{state_text}\n{amsg.ADM_ADD_MEDIA_CONFIRMATION}'
        await send_any_media_to_user_with_kb(bot=bot,
                                             user_tg_id=message.from_user.id,
                                             media_type=(await state.get_data()).get("media_type"),
                                             caption=message_text,
                                             file_id=(await state.get_data()).get("telegram_id"),
                                             reply_kb=await akb.admin_adding_media_kb(confirmation=True))
        await state.set_state(AddMedia.confirmation)
    else:
        # снова выводим схему изучения и предлагаем ввести день изучения
        schema = await get_shema_text_by_word_id((await state.get_data()).get("word_id"))
        state_text = await get_text_from_media_adding_state(state)
        message_text = f'{state_text}\n{amsg.ADM_ADD_MEDIA_DAY_REP}\n{schema}'
        reply_kb = await akb.admin_adding_media_kb(adding_study_day=STUDYING_DAY_LIST)
        await send_any_media_to_user_with_kb(bot=bot,
                                             user_tg_id=message.from_user.id,
                                             media_type=(await state.get_data()).get("media_type"),
                                             caption=message_text,
                                             file_id=(await state.get_data()).get("telegram_id"),
                                             reply_kb=reply_kb)
        await state.set_state(AddMedia.study_day)


# хендлер получения дня изучения с клавиатуры
@admin_adding_media_router.callback_query(F.data.startswith(callmsg.CALL_ADM_ADD_MEDIA_DAY), AddMedia.study_day)
async def admin_adding_media_capture_study_day_from_call(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека уровень
    study_day=call.data.replace(callmsg.CALL_ADM_ADD_MEDIA_DAY, '')
    await state.update_data(study_day=int(study_day))
    state_text = await get_text_from_media_adding_state(state)
    message_text = f'{state_text}\n{amsg.ADM_ADD_MEDIA_CONFIRMATION}'
    await send_any_media_to_user_with_kb(bot=bot,
                                         user_tg_id=call.from_user.id,
                                         media_type=(await state.get_data()).get("media_type"),
                                         caption=message_text,
                                         file_id=(await state.get_data()).get("telegram_id"),
                                         reply_kb=await akb.admin_adding_media_kb(confirmation=True))
    await call.answer()
    await state.set_state(AddMedia.confirmation)


# хендлер получения текста при ожидании подтверждения - возврат
@admin_adding_media_router.message(F.text, AddMedia.confirmation)
async def admin_adding_media_capture_confirmation_from_message(message: Message, state: FSMContext):
    state_text = await get_text_from_media_adding_state(state)
    message_text = f'{state_text}\n{amsg.ADM_ADD_MEDIA_CONFIRMATION_REP}'
    await send_any_media_to_user_with_kb(bot=bot,
                                         user_tg_id=message.from_user.id,
                                         media_type=(await state.get_data()).get("media_type"),
                                         caption=message_text,
                                         file_id=(await state.get_data()).get("telegram_id"),
                                         reply_kb=await akb.admin_adding_media_kb(confirmation=True))
    await state.set_state(AddMedia.confirmation)


# хендлер подтверждения записи с колбэка
@admin_adding_media_router.callback_query(F.data.startswith(callmsg.CALL_ADM_ADD_MEDIA_CONF), AddMedia.confirmation)
async def admin_adding_media_capture_confirmation_from_call(call: CallbackQuery, state: FSMContext):
    # получаем из колбека подтверждение
    confirm=call.data.replace(callmsg.CALL_ADM_ADD_MEDIA_CONF, '')
    if confirm==cmsg.YES:
        st_data = await state.get_data()
        word = st_data.get("word")
        word_id = st_data.get("word_id")
        author_id = st_data.get("author")
        collocation = st_data.get("collocation")
        level = st_data.get("level")
        media_type = st_data.get("media_type")
        caption = st_data.get("caption")
        telegram_id = st_data.get("telegram_id")
        study_day = st_data.get("study_day")
        res = await rq.add_media_to_db(media_type=media_type,
                                       word_id=word_id,
                                       collocation=collocation,
                                       caption=caption,
                                       telegram_id=telegram_id,
                                       study_day=study_day,
                                       author_id=author_id,
                                       level=level)
        # если все успешно записано
        if res:
            message_text = amsg.ADM_ADD_MEDIA_ADDED.format(word, collocation)
            # сохранение файла в папку
            if telegram_id:
                # Получаем media_id
                media_id = (await rq.get_medias_by_filters(telegram_id=telegram_id))[0].id
                # Выделяем файл, который хотим сохранить
                file = await bot.get_file(telegram_id)
                # Подпапка для сохранения
                path_name = datetime.now().strftime('%y-%m')
                # Проверяем наличие директории и создаем её, если её ещё нет

                if not os.path.exists(os.path.join(media_dir, path_name)):
                    os.makedirs(os.path.join(media_dir, path_name))
                # Даем название и путь этому файлу
                filename = f"{media_id}-{media_type}-{word}{os.path.splitext(file.file_path)[1]}"
                dest_path = os.path.join(media_dir, path_name, filename)
                # Скачиваем файл
                await bot.download_file(file.file_path, dest_path)
        else:
            message_text = amsg.ADM_ADD_MEDIA_ERROR
        reply_kb = await akb.admin_adding_menu_kb()
        await message_answer(source=call, message_text=message_text, reply_markup=reply_kb)

    elif confirm == cmsg.NO:
        await state.clear()
        word_list = await get_word_list_for_kb_with_ids()
        message_text = amsg.ADM_ADD_MEDIA_WORD_AGAIN
        reply_kb = await akb.admin_adding_media_kb(adding_word_list=word_list)
        await message_answer(source=call, message_text=message_text, reply_markup=reply_kb)
        await state.set_state(AddMedia.word)
    await call.answer()

