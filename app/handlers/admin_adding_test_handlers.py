from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from config import logger, STUDYING_DAY_LIST, TEST_TYPES

import app.keyboards.admin_keyboards as akb
import app.database.requests as rq
import data.admin_messages as amsg
import data.common_messages as cmsg
import app.handlers.callback_messages as callmsg

from app.utils.admin_utils import (get_shema_text_by_word_id,
                                   get_text_from_test_adding_state,
                                   get_word_list_for_kb_with_ids, message_answer)

admin_adding_test_router = Router()

class AddTest(StatesGroup):
    author = State()
    word = State()
    word_id = State()
    media_type = State()
    collocation = State()
    caption = State()
    study_day = State()
    confirmation = State()

# хендлер начала ввода теста, все начинается с выбора слова
@admin_adding_test_router.callback_query(F.data == amsg.ADMIN_BUTTON_ADD_TEST)
async def admin_adding_test_start(call: CallbackQuery, state: FSMContext):
    await state.clear()
    # получаем список слов
    word_list = await get_word_list_for_kb_with_ids()
    reply_kb = await akb.admin_adding_test_kb(adding_word_list=word_list)
    await call.message.edit_text(amsg.ADM_ADD_TEST_TEST, reply_markup=reply_kb)
    # заполняем ид автора
    user = await rq.get_users_by_filters(user_tg_id=call.from_user.id)
    await state.update_data(author=user.id)
    await call.answer()
    await state.set_state(AddTest.word)


# хендлер захвата слова из клавиатуры
@admin_adding_test_router.callback_query(F.data.startswith(callmsg.CALL_ADM_ADD_TEST_WORD), AddTest.word)
async def admin_adding_test_capture_word_from_call(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека слово
    word_call=call.data.replace(callmsg.CALL_ADM_ADD_TEST_WORD, '')
    # из базы данных забираем ид выбранного слова
    word_id = int(word_call.split('-', 1)[0])
    words = await rq.get_words_by_filters(word_id=word_id)
    await state.update_data(word=words[0].word)
    await state.update_data(word_id=words[0].id)
    await state.update_data(level=words[0].level)
    # вытаскиваем из стейта текст сообщения
    state_text = await get_text_from_test_adding_state(state)
    message_text = f'{state_text}\n{amsg.ADM_ADD_TEST_TYPE}'
    reply_kb = await akb.admin_adding_test_kb(adding_test_type_list=TEST_TYPES)
    await call.message.edit_text(text=message_text, reply_markup=reply_kb)
    await call.answer()
    await state.set_state(AddTest.media_type)


# хендлер захвата слова из текста
@admin_adding_test_router.message(F.text, AddTest.word)
async def admin_adding_test_capture_word_from_message(message: Message, state: FSMContext):
    # ищем слово в базе данных
    words = await rq.get_words_by_filters(word=message.text.lower())
    # если найдены и объект один, обновляем стейт, елсе по идее бессмысленен
    if words:
        if len(words)==1:
            await state.update_data(word=words[0].word)
            await state.update_data(word_id=words[0].id)
            await state.update_data(level=words[0].level)
            state_text = await get_text_from_test_adding_state(state)
            message_text = f'{state_text}\n{amsg.ADM_ADD_TEST_TYPE}'
            reply_kb = await akb.admin_adding_test_kb(adding_test_type_list=TEST_TYPES)
            await message.edit_text(text=message_text, reply_markup=reply_kb)
            await state.set_state(AddTest.media_type)
    # если не найдены, ищем по кусочкам
    else:
        words = await rq.get_words_by_filters(piece_of_word=message.text.lower())
        word_list = await get_word_list_for_kb_with_ids(words) if words else []
        reply_kb = await akb.admin_adding_test_kb(adding_word_list=word_list)
        message_text = amsg.ADM_ADD_TEST_WORD_NOT_FIND
        await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
        await state.set_state(AddTest.word)


# хендлер приема типа теста
@admin_adding_test_router.callback_query(F.data.startswith(callmsg.CALL_ADM_ADD_TEST_TYPE), AddTest.media_type)
async def admin_adding_test_capture_test_type_from_call(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека уровень
    test_type=call.data.replace(callmsg.CALL_ADM_ADD_TEST_TYPE, '')
    await state.update_data(media_type=test_type)
    message_text = await get_text_from_test_adding_state(state)

    if test_type == 'test4':
        await call.message.edit_text(f'{message_text}\n'
                                          f'Теперь напишите задание к тесту типа'
                                          f'"b_______ girl, butterfly, day"',
                                          reply_markup=await akb.admin_adding_test_kb())
        await state.set_state(AddTest.collocation)
    elif test_type == 'test7':
        shema = await get_shema_text_by_word_id((await state.get_data()).get("word_id"))
        await call.message.edit_text(f'{message_text}\n{shema}\n'
                                          f'Выберите день изучения',
                                          reply_markup=await akb.admin_adding_test_kb(adding_study_day=
                                                                                            STUDYING_DAY_LIST))
        await state.set_state(AddTest.study_day)
    else:
        logger.info('Неизвестный формат теста, обратитесь к администратору')
    await call.answer()


# хендлер приема уровня изучения с текста - не пропускает дальше
@admin_adding_test_router.message(F.text, AddTest.media_type)
async def admin_adding_test_capture_test_type_from_message(message: Message, state: FSMContext):
    reply_kb = await akb.admin_adding_test_kb(adding_test_type_list=TEST_TYPES)
    state_text = await get_text_from_test_adding_state(state)
    message_text = f'{state_text}\n{amsg.ADM_ADD_TEST_TYPE_REP}'
    await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
    await state.set_state(AddTest.media_type)


# хендлер приема коллокации
@admin_adding_test_router.message(F.text, AddTest.collocation)
async def admin_adding_test_capture_collocation(message: Message, state: FSMContext):
    # обновляем стейт
    await state.update_data(collocation=message.text.lower())

    reply_kb = await akb.admin_adding_test_kb(adding_study_day=STUDYING_DAY_LIST)
    state_text = await get_text_from_test_adding_state(state)
    schema = await get_shema_text_by_word_id((await state.get_data()).get("word_id"))
    message_text = f'{state_text}\n{amsg.ADM_ADD_TEST_DAY}\n{schema}\n'
    await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
    await state.set_state(AddTest.study_day)


# # хендлер приема дня теста  с текста
@admin_adding_test_router.message(F.text, AddTest.study_day)
async def admin_adding_test_capture_study_day_from_message(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(study_day=int(message.text))
        state_message_text = await get_text_from_test_adding_state(state)
        message_text = f'{state_message_text}\n{amsg.ADM_ADD_TEST_CONFIRMATION}'
        reply_kb = await akb.admin_adding_test_kb(confirmation=True)
        await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
        await state.set_state(AddTest.confirmation)
    else:
        state_text = await get_text_from_test_adding_state(state)
        schema = await get_shema_text_by_word_id((await state.get_data()).get("word_id"))
        message_text = f'{state_text}\n{amsg.ADM_ADD_TEST_DAY_REP}\n{schema}'
        reply_kb = await akb.admin_adding_test_kb(adding_study_day=STUDYING_DAY_LIST)
        await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
        await state.set_state(AddTest.study_day)


# хендлер получения дня изучения с call
@admin_adding_test_router.callback_query(F.data.startswith(callmsg.CALL_ADM_ADD_TEST_DAY), AddTest.study_day)
async def admin_adding_test_capture_study_day_from_call(call: CallbackQuery, state: FSMContext):
    # # вытаскиваем из колбека уровень
    study_day=call.data.replace(callmsg.CALL_ADM_ADD_TEST_DAY, '')
    await state.update_data(study_day=int(study_day))
    state_text = await get_text_from_test_adding_state(state)
    message_text = f'{state_text}\n{amsg.ADM_ADD_TEST_CONFIRMATION}'
    reply_kb = await akb.admin_adding_test_kb(confirmation=True)
    await call.message.edit_text(message_text, reply_markup=reply_kb)
    await call.answer()
    await state.set_state(AddTest.confirmation)


# хендлер получения текста при ожидании подтверждения - возврат
@admin_adding_test_router.message(F.text, AddTest.confirmation)
async def admin_adding_test_capture_confirmation_from_message(message: Message, state: FSMContext):
    state_text = await get_text_from_test_adding_state(state)
    message_text = f'{state_text}\n{amsg.ADM_ADD_TEST_CONFIRMATION_REP}'
    reply_kb = await akb.admin_adding_test_kb(confirmation=True)
    await message.edit_text(message_text, reply_markup=reply_kb)
    await state.set_state(AddTest.confirmation)


# хендлер подтверждения записи с колбэка
@admin_adding_test_router.callback_query(F.data.startswith(callmsg.CALL_ADM_ADD_TEST_CONF), AddTest.confirmation)
async def admin_adding_test_capture_confirmation_from_call(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека уровень
    confirm=call.data.replace(callmsg.CALL_ADM_ADD_TEST_CONF, '')
    if confirm==cmsg.YES:
        st_data = await state.get_data()
        word = st_data.get("word")
        word_id = st_data.get("word_id")
        author_id = st_data.get("author")
        collocation = st_data.get("collocation")
        level = st_data.get("level")
        media_type = st_data.get("media_type")
        caption = st_data.get("caption")
        study_day = st_data.get("study_day")

        res = await rq.add_media_to_db(media_type=media_type,
                                       word_id=word_id,
                                       collocation=collocation,
                                       caption=caption,
                                       study_day=study_day,
                                       author_id=author_id,
                                       level=level)

        message_text = amsg.ADM_ADD_TEST_ADDED.format(word, media_type) if res else amsg.ADM_ADD_TEST_ERROR
        reply_kb = await akb.admin_adding_menu_kb()
        await call.message.edit_text(message_text, reply_markup=reply_kb)
    elif confirm == cmsg.NO:
        await state.clear()
        word_list = await get_word_list_for_kb_with_ids()
        message_text = amsg.ADM_ADD_TEST_WORD_AGAIN
        reply_kb = await akb.admin_adding_test_kb(adding_word_list=word_list)
        await call.message.edit_text(message_text, reply_markup=reply_kb)
        await state.set_state(AddTest.word)

    await call.answer()

