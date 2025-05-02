from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
import app.keyboards.admin_keyboards as akb
import app.database.requests as rq
import data.admin_messages as amsg
import data.common_messages as cmsg
import app.handlers.callback_messages as callmsg
from app.utils.admin_utils import message_answer, get_text_from_word_adding_state


admin_adding_word_router = Router()


# #класс для ФСМ добавления слова в базу данных (таблицу "слова")
class AddWord(StatesGroup):
    word = State()
    level = State()
    definition = State()
    author = State()
    part = State()
    translation = State()
    confirmation = State()


# переход в из админского меню по нажатию на кнопку добавить слово
@admin_adding_word_router.callback_query(F.data == amsg.ADMIN_BUTTON_ADD_WORD)
async def admin_adding_word_start(call: CallbackQuery, state: FSMContext):
    # очищаем стейт
    await state.clear()
    reply_kb = await akb.admin_adding_word_kb()
    message_text = amsg.ADM_ADD_WORD_WORD
    await call.message.edit_text(text=message_text, reply_markup=reply_kb)
    await call.answer()
    await state.set_state(AddWord.word)


# хендлер получения слова
@admin_adding_word_router.message(F.text, AddWord.word)
async def admin_adding_word_capture_word(message: Message, state: FSMContext):
    # проверяем слово в базе данных
    # если оно там есть - пусть пробует снова
    if await rq.get_words_by_filters(word=message.text.lower().strip()):
        message_text = amsg.ADM_ADD_WORD_WORD_FIND
        reply_kb = await akb.admin_adding_word_kb()
        await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
        await state.set_state(AddWord.word)
    # если нет - запоминаем в стейт слово и ид юзера из бд
    else:
        await state.update_data(word=message.text.lower().strip())
        user = await rq.get_users_by_filters(user_tg_id=message.from_user.id)
        await state.update_data(author=user.id)
        # приглашаем выбрать уровень слова
        state_text = await get_text_from_word_adding_state(state)
        message_text = f'{state_text}\n{amsg.ADM_ADD_WORD_LEVEL}'
        reply_kb = await akb.admin_adding_word_kb(adding_level=True)
        await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
        await state.set_state(AddWord.level)


# хендлер получения уровня
@admin_adding_word_router.callback_query(F.data.startswith(callmsg.CALL_ADM_ADD_WORD_LEVEL), AddWord.level)
async def admin_adding_word_capture_level(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека уровень, запоминаем, приглашаем ввести часть речи
    level=call.data.replace(callmsg.CALL_ADM_ADD_WORD_LEVEL, '')
    await state.update_data(level=level)
    state_text = await get_text_from_word_adding_state(state)
    message_text = f'{state_text}\n{amsg.ADM_ADD_WORD_PART}'
    reply_kb = await akb.admin_adding_word_kb(adding_part=True)
    await call.message.edit_text(message_text, reply_markup=reply_kb)
    await call.answer()
    await state.set_state(AddWord.part)


# хендлер получения уровня, если что-то вписано с клавиатуры - отправляем снова на кнопки
@admin_adding_word_router.message(F.text, AddWord.level)
async def admin_adding_word_capture_level_from_text(message: Message, state: FSMContext):
    # даже не обрабатываем ввод - сразу приглашаем обратно выбрать с клавиатуры
    state_text = await get_text_from_word_adding_state(state)
    message_text = f'{state_text}\n{amsg.ADM_ADD_WORD_INV_KB}'
    reply_kb = await akb.admin_adding_word_kb(adding_level=True)
    await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
    await state.set_state(AddWord.level)


# хендлер получения части речи
@admin_adding_word_router.callback_query(F.data.startswith(callmsg.CALL_ADM_ADD_WORD_PART), AddWord.part)
async def admin_adding_word_capture_part(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека часть речи, запоминаем, приглашаем ввести определение
    part=call.data.replace(callmsg.CALL_ADM_ADD_WORD_PART, '')
    await state.update_data(part=part)
    state_text = await get_text_from_word_adding_state(state)
    message_text = f'{state_text}\n{amsg.ADM_ADD_WORD_DEFINITION}'
    reply_kb = await akb.admin_adding_word_kb()
    await call.message.edit_text(message_text, reply_markup=reply_kb)
    await call.answer()
    await state.set_state(AddWord.definition)


# хендлер получения части речи, если что-то вписано с клавиатуры - отправляем снова на кнопки
@admin_adding_word_router.message(F.text, AddWord.part)
async def admin_adding_word_capture_part_from_text(message: Message, state: FSMContext):
    # не обрабатывая введенное - сразу отправляем снова на кнопки
    state_text = await get_text_from_word_adding_state(state)
    message_text = f'{state_text}\n{amsg.ADM_ADD_WORD_INV_KB}'
    reply_kb = await akb.admin_adding_word_kb(adding_part=True)
    await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
    await state.set_state(AddWord.part)


# хендлер получения определения
@admin_adding_word_router.message(F.text, AddWord.definition)
async def admin_adding_word_capture_definition(message: Message, state: FSMContext):
    # обработки длины - ограничение на show_alert телеграмма
    if len(message.text) > 190:
        state_text = await get_text_from_word_adding_state(state)
        message_text = amsg.ADM_ADD_WORD_INV_LEN(format(state_text, str(len(message.text))))
        reply_kb = await akb.admin_adding_word_kb()
        await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
        await state.set_state(AddWord.definition)
    # если длина ОК - записываем в стейт и приглашаем ввести перевод
    else:
        await state.update_data(definition=message.text.lower().strip())
        state_text = await get_text_from_word_adding_state(state)
        message_text = f'{state_text}\n{amsg.ADM_ADD_WORD_TRANSLATION}'
        reply_kb = await akb.admin_adding_word_kb()
        await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
        await state.set_state(AddWord.translation)


# хендлер получения перевода
@admin_adding_word_router.message(F.text, AddWord.translation)
async def admin_adding_word_capture_translation(message: Message, state: FSMContext):
    # обработки длины - ограничение на show_alert телеграмма
    if len(message.text) > 190:
        state_text = await get_text_from_word_adding_state(state)
        message_text = amsg.ADM_ADD_WORD_INV_LEN(format(state_text, str(len(message.text))))
        reply_kb = await akb.admin_adding_word_kb()
        await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
        await state.set_state(AddWord.translation)
    # если длина ОК - записываем в стейт и приглашаем к подтверждению
    else:
        await state.update_data(translation=message.text.lower().strip())
        state_text = await get_text_from_word_adding_state(state)
        message_text = f'{state_text}\n{amsg.ADM_INV_INP_WORD_CONFIRMATION}'
        reply_kb = await akb.admin_adding_word_kb(confirmation=True)
        await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
        await state.set_state(AddWord.confirmation)


# хендлер получения текста при ожидании подтверждения - возврат
@admin_adding_word_router.message(F.text, AddWord.confirmation)
async def admin_adding_word_capture_confirmation_from_message(message: Message, state: FSMContext):
    state_text = await get_text_from_word_adding_state(state)
    message_text = f'{state_text}\n{amsg.ADM_INV_INP_WORD_CONFIRMATION_REP}'
    reply_kb = await akb.admin_adding_word_kb(confirmation=True)
    await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
    await state.set_state(AddWord.confirmation)


# хендлер получения подтверждения ввода
@admin_adding_word_router.callback_query(F.data.startswith(callmsg.CALL_ADM_ADD_WORD_CONF), AddWord.confirmation)
async def admin_adding_word_capture_confirmation(call: CallbackQuery, state: FSMContext):
    # вытаскиваем из колбека ответ на подтверждение
    confirm=call.data.replace(callmsg.CALL_ADM_ADD_WORD_CONF, '')
    # если да - получаем все из стейта, записываем в базу данных
    if confirm==cmsg.YES:
        st_data = await state.get_data()
        word = st_data.get("word")
        level = st_data.get("level")
        part = st_data.get("part")
        definition = st_data.get("definition")
        translation = st_data.get("translation")
        author_id = st_data.get("author")
        # вносим в базу данных, функция должна вернуть тру, сообщаем о внесении или ошибке, очищаем стейт
        res = await rq.add_word_to_db(word = word, level=level, part=part, translation=translation,
                                      definition=definition, author_id=author_id)
        # ответ либо о добавлении либо об ошибке
        message_text = amsg.ADM_INV_INP_WORD_ADDED.format(word) if res else amsg.ADM_INV_INP_WORD_ERROR
        reply_kb = await akb.admin_adding_menu_kb()
        await call.message.edit_text(text=message_text, reply_markup=reply_kb)
        await call.answer()
        await state.clear()
    # если автор отказался вводить - отправляем на ввод сначала
    elif confirm == cmsg.NO:
        await state.clear()
        message_text = amsg.ADM_INV_INP_WORD_WORD_AGAIN
        reply_kb = await akb.admin_adding_word_kb()
        await call.message.edit_text(text=message_text, reply_markup=reply_kb)
        await call.answer()
        await state.set_state(AddWord.word)

