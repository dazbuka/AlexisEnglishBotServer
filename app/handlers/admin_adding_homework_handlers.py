import re
from curses.ascii import isdigit
from aiogram.fsm.state import State, StatesGroup
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
from app.utils.admin_utils import get_text_from_homework_adding_state
import app.utils.admin_utils as aut
from app.utils.admin_utils import message_answer
import app.database.requests as rq
import app.keyboards.admin_keyboards as akb
import app.handlers.callback_messages as callmsg
import data.common_messages as cmsg
import data.admin_messages as amsg


admin_adding_homework_router = Router()

class AddHomework(StatesGroup):
    author = State()
    hometask = State()
    date = State()
    users_kb = State()
    confirmation = State()


@admin_adding_homework_router.callback_query(F.data == amsg.ADMIN_BUTTON_ADD_HOMEWORK)
async def admin_adding_homework_start(call: CallbackQuery, state: FSMContext):
    user = await rq.get_users_by_filters(user_tg_id=call.from_user.id)
    await state.update_data(author=user.id)
    state_text = await aut.get_text_from_homework_adding_state(state)
    message_text = f'{state_text}\n{amsg.ADM_ADD_HOMEWORK_HOMETASK}'
    reply_kb = await akb.admin_adding_homework_kb()
    await call.message.edit_text(message_text, reply_markup=reply_kb)
    await state.set_state(AddHomework.hometask)
    await call.answer()


@admin_adding_homework_router.message(F.text, AddHomework.hometask)
async def admin_adding_homework_capture_hometask(message: Message, state: FSMContext):
    await state.update_data(hometask=message.text.strip())
    state_text = await get_text_from_homework_adding_state(state)
    message_text = f'{state_text}\n{amsg.ADM_ADD_HOMEWORK_USERS}'
    user_list = await aut.get_users_list_for_kb_with_limit()
    await state.update_data(users_kb=user_list)
    reply_kb = await akb.admin_adding_homework_kb(adding_user_list=user_list)
    await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
    await state.set_state(AddHomework.users_kb)


# хендлер захвата слова из клавиатуры
@admin_adding_homework_router.callback_query(F.data.startswith(callmsg.CALL_ADM_ADD_HOME_USER), AddHomework.users_kb)
async def admin_adding_homework_capture_users_from_call(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека слово
    user_call=call.data.replace(callmsg.CALL_ADM_ADD_HOME_USER, '')
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
        state_text = await aut.get_text_from_homework_adding_state(state)
        message_text = f'{state_text}\n{amsg.ADM_ADD_HOMEWORK_DAY}'
        reply_kb = await akb.admin_adding_homework_kb(adding_study_day=True)
        await call.message.edit_text(message_text, reply_markup=reply_kb)
        await state.set_state(AddHomework.date)
        await call.answer()
    else:
        users_list=await aut.set_check_in_list(checked_list=users_list, checked_item=user_call)
        message_text = amsg.ADM_ADD_HOMEWORK_MORE
        reply_kb = await akb.admin_adding_homework_kb(adding_user_list=users_list)
        await call.message.edit_text(message_text, reply_markup=reply_kb)
        await state.update_data(users_kb=users_list)
        await state.set_state(AddHomework.users_kb)
        await call.answer()


@admin_adding_homework_router.message(F.text, AddHomework.users_kb)
async def admin_adding_homework_returning_from_message(message: Message, state: FSMContext):
    user_list = (await state.get_data()).get('users_kb')
    message_text = amsg.ADM_ADD_HOMEWORK_MORE
    reply_kb = await akb.admin_adding_homework_kb(adding_user_list=user_list)
    await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
    await state.set_state(AddHomework.users_kb)


# хендлер захвата слова из клавиатуры
@admin_adding_homework_router.callback_query(F.data.startswith(callmsg.CALL_ADM_ADD_HOME_DAY), AddHomework.date)
async def admin_adding_homework_capture_day_from_call(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека слово
    day=call.data.replace(callmsg.CALL_ADM_ADD_HOME_DAY, '')
    await state.update_data(date=day)
    state_text = await aut.get_text_from_homework_adding_state(state)
    message_text = f'{state_text}\n{amsg.ADM_ADD_HOMEWORK_CONFIRMATION}'
    reply_kb = await akb.admin_adding_homework_kb(confirmation=True)
    await call.message.edit_text(message_text, reply_markup=reply_kb)
    await state.set_state(AddHomework.confirmation)
    await call.answer()


@admin_adding_homework_router.message(F.text, AddHomework.date)
async def admin_adding_homework_capture_day_from_message(message: Message, state: FSMContext):
    # вытаскиваем из дату из сообщения
    date=message.text.strip()
    pattern = r'\d{1,2}\.\d{1,2}\.\d{4}'
    if re.match(pattern, date):
        await state.update_data(date=date)
        state_text = await aut.get_text_from_homework_adding_state(state)
        message_text = f'{state_text}\n{amsg.ADM_ADD_HOMEWORK_CONFIRMATION}'
        reply_kb = await akb.admin_adding_homework_kb(confirmation=True)
        await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
        await state.set_state(AddHomework.confirmation)
    else:
        state_text = await aut.get_text_from_homework_adding_state(state)
        message_text = f'{state_text}\n{amsg.ADM_ADD_HOMEWORK_DAY}'
        reply_kb = await akb.admin_adding_homework_kb(adding_study_day=True)
        await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
        await state.set_state(AddHomework.date)


@admin_adding_homework_router.callback_query(F.data.startswith(callmsg.CALL_ADM_ADD_HOME_CONF),
                                             AddHomework.confirmation)
async def admin_adding_homework_capture_confirmation_from_call(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека уровень
    confirm = call.data.replace(callmsg.CALL_ADM_ADD_HOME_CONF, '')
    if confirm == cmsg.YES:
        st_data = await state.get_data()
        hometask = st_data.get("hometask")
        users_list = st_data.get("users_kb")
        author_id = st_data.get("author")
        date = datetime.strptime(st_data.get("date"), "%d.%m.%Y")
        hw_day = datetime.combine(date, datetime.now().time())
        users = [int(x.split('-', 1)[0]) for x in users_list]
        users_for_db = ','.join(map(str, users))
        users_text = '\n'.join(map(str, st_data.get("users_kb")))
        res = await rq.set_homework(hometask=hometask, homework_date=hw_day, author_id=author_id, users=users_for_db)

        if res:
            message_text = amsg.ADM_ADD_HOMEWORK_ADDED.format(hometask, users_text)
        else:
            message_text = amsg.ADM_ADD_HOMEWORK_ERROR

        reply_kb = await akb.admin_adding_menu_kb()
        await call.message.edit_text(message_text, reply_markup=reply_kb)
        await call.answer()

    elif confirm == cmsg.NO:
        await state.clear()
        reply_kb = await akb.admin_adding_homework_kb()
        message_text = amsg.ADM_ADD_HOMEWORK_HOMETASK_AGAIN
        user = await rq.get_users_by_filters(user_tg_id=call.from_user.id)
        await state.update_data(author=user.id)
        await call.message.edit_text(message_text, reply_markup=reply_kb)
        await call.answer()





