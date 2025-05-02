from curses.ascii import isdigit
from app.utils.admin_utils import message_answer
import re
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from datetime import datetime, timedelta

import app.keyboards.admin_keyboards as akb
import app.database.requests as rq
import data.admin_messages as amsg
import data.common_messages as cmsg
import app.handlers.callback_messages as callmsg

import app.utils.admin_utils as aut

admin_adding_task_router = Router()

class AddTask(StatesGroup):
    author = State()
    words_kb = State()
    medias_kb = State()
    users_kb = State()
    beginning_date = State()
    confirmation = State()


@admin_adding_task_router.callback_query(F.data == amsg.ADMIN_BUTTON_ADD_TASK)
async def admin_adding_task_start(call: CallbackQuery, state: FSMContext):
    await state.clear()
    message_text = amsg.ADM_ADD_TASK
    reply_kb = await akb.admin_adding_task_menu_kb()
    await call.message.edit_text(message_text, reply_markup=reply_kb)
    await call.answer()


# хендлер начала ввода теста, все начинается с выбора слова
@admin_adding_task_router.callback_query(F.data == amsg.ADMIN_BUTTON_ADD_TASK_MEDIA)
@admin_adding_task_router.callback_query(F.data == amsg.ADMIN_BUTTON_ADD_TASK_SHEMA)
async def admin_adding_task_start(call: CallbackQuery, state: FSMContext):
    await state.clear()
    # получаем список слов или медиа
    if call.data == amsg.ADMIN_BUTTON_ADD_TASK_SHEMA:
        word_list = await aut.get_word_list_for_kb_with_ids(limit=90)
        reply_kb = await akb.admin_adding_task_kb(adding_word_list=word_list)
        message_text = amsg.ADM_ADD_TASK_WORD
        await state.update_data(words_kb=word_list)
        await state.set_state(AddTask.words_kb)
    elif call.data == amsg.ADMIN_BUTTON_ADD_TASK_MEDIA:
        media_list = await aut.get_medias_list_for_kb_with_limit(media_only=False, limit=90)
        reply_kb = await akb.admin_adding_task_kb(adding_media_list=media_list)
        message_text = amsg.ADM_ADD_TASK_MEDIA
        await state.update_data(medias_kb=media_list)
        await state.set_state(AddTask.medias_kb)

    user = await rq.get_users_by_filters(user_tg_id=call.from_user.id)
    await state.update_data(author=user.id)
    await call.message.edit_text(message_text, reply_markup=reply_kb)
    await call.answer()


# хендлер захвата слова из клавиатуры кнопок!
@admin_adding_task_router.callback_query(F.data.startswith(callmsg.CALL_ADM_ADD_TASK_WORD), AddTask.words_kb)
async def admin_adding_task_capture_words_from_call(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека слова
    word_call=call.data.replace(callmsg.CALL_ADM_ADD_TASK_WORD, '')
    # вытаскиваем массив слов из стейта
    words_list = (await state.get_data()).get('words_kb')
    # если конец ввода
    # костыль, не позволяющий пройти дальше не выбрав ничего
    have_check = False
    for word in words_list:
        if not isdigit(word[0]):
            have_check=True
    if word_call == callmsg.CALL_ADMIN_END_CHOOSING and have_check:
        # убираем
        new_word_list = await aut.get_list_from_check_list(words_list)
        await state.update_data(words_kb=new_word_list)
        # вытаскиваем из стейта текст сообщения
        state_text = await aut.get_text_from_task_adding_state(state)
        message_text = f'{state_text}\n{amsg.ADM_ADD_TASK_USERS}'
        user_list = await aut.get_users_list_for_kb_with_limit()
        reply_kb =await akb.admin_adding_task_kb(adding_user_list=user_list)
        await call.message.edit_text(message_text, reply_markup=reply_kb)
        await state.update_data(users_kb=user_list)
        await state.set_state(AddTask.users_kb)
        await call.answer()
    else:
        words_list = await aut.set_check_in_list(checked_list=words_list, checked_item=word_call)# плюс или минус кружок
        message_text = amsg.ADM_ADD_ADDING_MORE
        reply_kb = await akb.admin_adding_task_kb(adding_word_list=words_list)
        await call.message.edit_text(message_text, reply_markup=reply_kb)
        await state.update_data(words_kb=words_list)
        await state.set_state(AddTask.words_kb)
        await call.answer()


# хендлеры защита от печати
@admin_adding_task_router.message(F.text, AddTask.words_kb)
async def admin_adding_task_returning_from_message(message: Message, state: FSMContext):
    words_list = (await state.get_data()).get('words_kb')
    message_text = amsg.ADM_ADD_ADDING_MORE
    reply_kb = await akb.admin_adding_task_kb(adding_word_list=words_list)
    await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
    await state.set_state(AddTask.words_kb)


# хендлер захвата слова из клавиатуры
@admin_adding_task_router.callback_query(F.data.startswith(callmsg.CALL_ADM_ADD_TASK_MEDIA), AddTask.medias_kb)
async def admin_adding_task_capture_medias_from_call(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека слова
    media_call=call.data.replace(callmsg.CALL_ADM_ADD_TASK_MEDIA, '')
    # вытаскиваем массив слов из стейта
    medias_list = (await state.get_data()).get('medias_kb')
    # костыль, не позволяющий пройти дальше не выбрав ничего
    have_check = False
    for medias in medias_list:
        if not isdigit(medias[0]):
            have_check = True
    # если конец ввода
    if media_call == callmsg.CALL_ADMIN_END_CHOOSING and have_check:
        # убираем
        new_media_list = await aut.get_list_from_check_list(medias_list)
        await state.update_data(medias_kb=new_media_list)
        # вытаскиваем из стейта текст сообщения
        state_text = await aut.get_text_from_task_adding_state(state)
        message_text = f'{state_text}\n{amsg.ADM_ADD_TASK_USERS}'
        user_list = await aut.get_users_list_for_kb_with_limit()
        reply_kb = await akb.admin_adding_task_kb(adding_user_list=user_list)
        await call.message.edit_text(message_text, reply_markup=reply_kb)
        await state.update_data(users_kb=user_list)
        await state.set_state(AddTask.users_kb)
        await call.answer()
    else:
        medias_list = await aut.set_check_in_list(checked_list=medias_list, checked_item=media_call)
        message_text = amsg.ADM_ADD_ADDING_MORE
        reply_kb = await akb.admin_adding_task_kb(adding_media_list=medias_list)
        await call.message.edit_text(message_text, reply_markup=reply_kb)
        await state.update_data(medias_kb=medias_list)
        await state.set_state(AddTask.medias_kb)
        await call.answer()


@admin_adding_task_router.message(F.text, AddTask.medias_kb)
async def admin_adding_task_returning_from_message(message: Message, state: FSMContext):
    medias_list = (await state.get_data()).get('medias_kb')
    message_text = amsg.ADM_ADD_ADDING_MORE
    reply_kb = await akb.admin_adding_task_kb(adding_media_list=medias_list)
    await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
    await state.set_state(AddTask.medias_kb)


# хендлер захвата слова из клавиатуры
@admin_adding_task_router.callback_query(F.data.startswith(callmsg.CALL_ADM_ADD_TASK_USER), AddTask.users_kb)
async def admin_adding_task_capture_users_from_call(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека слово
    user_call=call.data.replace(callmsg.CALL_ADM_ADD_TASK_USER, '')
    users_list = (await state.get_data()).get('users_kb')
    # костыль, не позволяющий пройти дальше не выбрав ничего
    have_check = False
    for user in users_list:
        if not isdigit(user[0]):
            have_check = True

    if user_call == callmsg.CALL_ADMIN_END_CHOOSING and have_check:
        new_user_list = await aut.get_list_from_check_list(users_list)
        await state.update_data(users_kb=new_user_list)
        # вытаскиваем из стейта текст сообщения
        state_text = await aut.get_text_from_task_adding_state(state)
        message_text = f'{state_text}\n{amsg.ADM_ADD_TASK_DAY}'
        reply_kb = await akb.admin_adding_task_kb(adding_study_day=True)
        await call.message.edit_text(message_text, reply_markup=reply_kb)
        await state.set_state(AddTask.beginning_date)
        await call.answer()
    else:
        users_list=await aut.set_check_in_list(checked_list=users_list, checked_item=user_call)
        message_text = amsg.ADM_ADD_ADDING_MORE
        reply_kb = await akb.admin_adding_task_kb(adding_user_list=users_list)
        await call.message.edit_text(message_text, reply_markup=reply_kb)
        await state.update_data(users_kb=users_list)
        await state.set_state(AddTask.users_kb)
        await call.answer()


@admin_adding_task_router.message(F.text, AddTask.users_kb)
async def admin_adding_task_returning_from_message(message: Message, state: FSMContext):
    user_list = (await state.get_data()).get('users_kb')
    message_text = amsg.ADM_ADD_ADDING_MORE
    reply_kb = await akb.admin_adding_task_kb(adding_user_list=user_list)
    await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
    await state.set_state(AddTask.users_kb)


# хендлер захвата слова из клавиатуры
@admin_adding_task_router.callback_query(F.data.startswith(callmsg.CALL_ADM_ADD_TASK_DAY), AddTask.beginning_date)
async def admin_adding_task_capture_day_from_call(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека слово
    day=call.data.replace(callmsg.CALL_ADM_ADD_TASK_DAY, '')
    await state.update_data(beginning_date=day)
    state_text = await aut.get_text_from_task_adding_state(state)
    message_text = f'{state_text}\n{amsg.ADM_ADD_TEST_CONFIRMATION}'
    reply_kb = await akb.admin_adding_task_kb(confirmation=True)
    await call.message.edit_text(message_text, reply_markup=reply_kb)
    await state.set_state(AddTask.confirmation)
    await call.answer()


@admin_adding_task_router.message(F.text, AddTask.beginning_date)
async def admin_adding_task_capture_day_from_message(message: Message, state: FSMContext):
    # вытаскиваем из дату из сообщения
    date=message.text.strip()
    pattern = r'\d{1,2}\.\d{1,2}\.\d{4}'
    if re.match(pattern, date):
        await state.update_data(beginning_date=date)
        state_text = await aut.get_text_from_task_adding_state(state)
        message_text = f'{state_text}\n{amsg.ADM_ADD_TEST_CONFIRMATION}'
        reply_kb = await akb.admin_adding_task_kb(confirmation=True)
        await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
        await state.set_state(AddTask.confirmation)
    else:
        state_text = await aut.get_text_from_task_adding_state(state)
        message_text = f'{state_text}\n{amsg.ADM_ADD_TASK_DAY}'
        reply_kb = await akb.admin_adding_task_kb(adding_study_day=True)
        await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
        await state.set_state(AddTask.beginning_date)


@admin_adding_task_router.callback_query(F.data.startswith(callmsg.CALL_ADM_ADD_TASK_CONF),
                                         AddTask.confirmation)
async def admin_adding_task_capture_confirmation_from_call(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека уровень
    confirm = call.data.replace(callmsg.CALL_ADM_ADD_TASK_CONF, '')
    if confirm == cmsg.YES:
        st_data = await state.get_data()
        words_list = st_data.get("words_kb")
        medias_list = st_data.get("medias_kb")
        users_list = st_data.get("users_kb")
        author = st_data.get("author")
        beginning_date = st_data.get("beginning_date")
        users = [int(x.split('-', 1)[0]) for x in users_list]

        res = False
        text = ''

        if words_list:
            words = [int(x.split('-', 1)[0]) for x in words_list]
            for word in words:
                medias = await rq.get_medias_by_filters(word_id=word)
                for media in medias:
                    date = datetime.strptime(beginning_date, "%d.%m.%Y") + timedelta(media.study_day - 1)
                    study_day = datetime.combine(date, datetime.now().time())
                    for user in users:
                        res = await rq.set_task(user_id=user, media_id=media.id, task_time=study_day, author_id=author)

            text = '\n'.join(map(str, st_data.get("words_kb")))

        elif medias_list:
            medias = [int(x.split('-', 1)[0]) for x in medias_list]
            study_day = datetime.combine(datetime.strptime(beginning_date, "%d.%m.%Y"), datetime.now().time())
            for user in users:
                for media in medias:
                    res = await rq.set_task(user_id=user, media_id=media, task_time=study_day, author_id=author)
            text = '\n'.join(map(str, st_data.get("medias_kb")))

        users_text = '\n'.join(map(str, st_data.get("users_kb")))
        if res:
            message_text = amsg.ADM_ADD_TASK_ADDED_MEDIA.format(text, users_text)
        else:
            message_text = amsg.ADM_ADD_TASK_ERROR

        reply_kb = await akb.admin_adding_menu_kb()
        await call.message.edit_text(message_text, reply_markup=reply_kb)
        await call.answer()

    elif confirm == cmsg.NO:
        st_data = await state.get_data()
        words_list = st_data.get("words_kb")
        medias_list = st_data.get("medias_kb")
        await state.clear()
        if words_list:
            word_list = await aut.get_word_list_for_kb_with_ids()
            reply_kb = await akb.admin_adding_task_kb(adding_word_list=word_list)
            message_text = amsg.ADM_ADD_TASK_WORD_AGAIN
            await state.update_data(words_kb=word_list)
            await state.set_state(AddTask.words_kb)

        elif medias_list:
            media_list = await aut.get_medias_list_for_kb_with_limit(media_only=False)
            reply_kb = await akb.admin_adding_task_kb(adding_media_list=media_list)
            message_text = amsg.ADM_ADD_TASK_MEDIA_AGAIN
            await state.update_data(medias_kb=media_list)
            await state.set_state(AddTask.medias_kb)

        user = await rq.get_users_by_filters(user_tg_id=call.from_user.id)
        await state.update_data(author=user.id)
        await call.message.edit_text(message_text, reply_markup=reply_kb)
        await call.answer()







