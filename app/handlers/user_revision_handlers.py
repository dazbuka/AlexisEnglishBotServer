from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from config import logger
from app.utils.admin_utils import count_user_tasks_by_tg_id, message_answer
import app.utils.user_utils as uut
import app.database.requests as rq
import app.keyboards.user_keyboards as ukb
import app.handlers.callback_messages as callmsg
import data.user_messages as umsg
import data.common_messages as cmsg

user_revision_router = Router()


# хендлер перехода в меню ревижн - пункт главного меню
@user_revision_router.callback_query(F.data == cmsg.COMMON_BUTTON_REVISION)
async def check_user_tasks(call : CallbackQuery, state: FSMContext):
    # сообщение логгеру
    logger.info(f'{call.from_user.username} ({call.from_user.first_name})'
                f' - вход в меню revision по *{call.data}*')
    # очищаем стейт
    await state.clear()
    # подсчитываем задания
    tasks_counter = await count_user_tasks_by_tg_id(user_tg_id=call.from_user.id)
    all_count = tasks_counter['all']
    next_task_id = tasks_counter['last_sent']
    # клавиатура для дальнейшего вывода
    reply_kb = await ukb.inline_revision_menu(next_task_id=next_task_id)
    # проверяем были ли вообще задания хоть какие-нибудь
    if all_count != 0:
        message_text = umsg.USER_INVITE_PRESS_ANY_BUTTON
        await message_answer(source=call, message_text=message_text, reply_markup=reply_kb)
    else:
        message_text = umsg.USER_REVISION_ANSWER_NO_REVISION
        reply_kb = await ukb.common_main_kb(user_tg_id= call.from_user.id)
        await message_answer(source=call, message_text=message_text, reply_markup=reply_kb)
    await call.answer()


# инлайн кнопка - колбэк реакция на нажатие пункта меню просмотр ревижн
@user_revision_router.callback_query(F.data == umsg.USER_REVISION_BUTTON_SHOW_LAST_WORDS)
async def show_last_words(call: CallbackQuery):
    # логгер
    logger.info(f'{call.message.from_user.username} ({call.message.from_user.first_name})'
                f' - выбрал пункт меню просмотр слов из *{call.data}*')
    # получаем задания пользователя, пусть 80, чтобы туда попало побольше слов
    tasks = await rq.get_tasks_by_filters(user_tg_id=call.from_user.id,
                                          limit=300)
    # получаем список слов из этих заданий и сортируем по алфавиту
    word_list = []
    if tasks:
        for task in tasks:
            word = await rq.get_words_by_filters(word_id=task.media.word_id)
            word_list.append(word[0].word)
    word_list=sorted(list(set(word_list)))
    # отправляем пользователю
    message_text = umsg.USER_INVITE_CHOOSE_AND_PRESS_ANY
    reply_kb = await ukb.inline_revision_word_buttons_kb(word_list)
    await message_answer(source=call, message_text=message_text, reply_markup=reply_kb)
    await call.answer()


# инлайн кнопка - реакция на выбор слова в ревижене
@user_revision_router.callback_query(F.data.startswith(callmsg.CALL_REVISION_WORD))
async def show_revision_word_list(call: CallbackQuery):
    # вытаскиваем из колбэка выбранное слово
    word = call.data.replace(callmsg.CALL_REVISION_WORD, '')
    # сообщение logger
    logger.info(f'{call.from_user.username} ({call.from_user.first_name})'
                f' - выбрал слово {word}')
    # подтягиваем список библиотеку коллокацией без тестов к этому слову, потом его передадим в клавиатуру
    media_list = await rq.get_medias_by_filters(word=word, media_only=True)
    collocation_list = []
    for media in media_list:
        collocation_list.append([media.id, media.collocation])
    # ответ для выбора коллокаций, клавиатура - список
    message_text = umsg.USER_INVITE_CHOOSE_AND_PRESS_ANY
    reply_kb = await ukb.inline_revision_collocations_buttons_kb(collocation_list)
    await message_answer(source=call, message_text=message_text, reply_markup=reply_kb)
    await call.answer()


# реакция на инлайн кнопки выбора коллокации для просмотра
@user_revision_router.callback_query(F.data.startswith(callmsg.CALL_REVISION_COLLOCATION))
async def show_revision_collocation_list(call: CallbackQuery):
    # вытаскиваем из колбэка номер коллокации, определяем по нему медиа
    colloc_num = int(call.data.replace(callmsg.CALL_REVISION_COLLOCATION, ''))
    sent_medias = await rq.get_medias_by_filters(media_id=colloc_num)
    # сообщение logger
    sent_media = sent_medias[0] if len(sent_medias)==1 else None
    logger.info(f'{call.from_user.username} ({call.from_user.first_name})'
                f' - выбрал коллокацию {sent_media.collocation}')
    # снова формируем клавиатуру
    media_list = await rq.get_medias_by_filters(word=sent_media.word.word, media_only=True)
    collocation_list = []
    for media in media_list:
        collocation_list.append([media.id, media.collocation])
    reply_kb = await ukb.inline_revision_collocations_buttons_kb(collocation_list)
    # отправляем пользователю медиа к коллокации
    await uut.send_media_to_user_call_with_kb(media=sent_media, call=call, reply_kb=reply_kb, with_de_tr=True)

    logger.info(f'{call.from_user.username} ({call.from_user.first_name})'
                f' - коллокация {sent_media.collocation} пользователю отправлена')
    await call.answer()


# просмотр пройденных заданий
@user_revision_router.callback_query(F.data.startswith(umsg.USER_REVISION_BUTTON_SHOW_LAST_TASKS))
async def show_last_medias(call: CallbackQuery):
    # логгер
    logger.info(f'{call.message.from_user.username} ({call.message.from_user.first_name}) '
                f' - выбрал пункт меню просмотр последний заданий *{call.data}*')
    # вытаскиваем из колбэка номер задания
    task_id = int(call.data.replace(umsg.USER_REVISION_BUTTON_SHOW_LAST_TASKS, ''))
    # получаем все задания пользователя
    tasks = await rq.get_tasks_by_filters(task_id=task_id)
    task = tasks[0]
    user = await rq.get_users_by_filters(user_tg_id=call.from_user.id)
    all_user_tasks = await rq.get_tasks_by_filters(user_id=user.id,
                                                   media_task_only=True,
                                                   sent=True)

    # делаем массив из индексов заданий
    task_num_list=[]
    if all_user_tasks:
        for item in all_user_tasks:
            task_num_list.append(item.id)
    # индекс текущего задания
    ind = task_num_list.index(task_id)
    # определяем индексы предыдущего и следующего задания чтобы передавать в колл
    if ind-1 == -len(task_num_list):
        previous_task_id = len(task_num_list)-1
    else:
        previous_task_id = task_num_list[ind - 1]
    # следующее
    if ind+1 == len(task_num_list):
        next_task_id = task_num_list[0]
    else:
        next_task_id = task_num_list[ind + 1]
    # отвечаем на колбэк, если нулевое алярм самое старое изученнное
    if ind == 0:
        await call.answer(umsg.USER_REVISION_ALARM_FIRST_TASK_OPENED, show_alert=True)
    else:
        await call.answer()
    # keyboard
    reply_kb = await ukb.inline_revision_tasks_menu(previous_task_id=previous_task_id,
                                                    next_task_id=next_task_id,
                                                    word_id=task.media.word_id,
                                                    media_id=task.media_id)
    t = task.time.date().strftime('%d.%m.%Y')
    added_text = f'\nStudy date: {t}'
    # отправляем пользователю
    await uut.send_media_to_user_call_with_kb(media=task.media,
                                              call=call,
                                              reply_kb=reply_kb,
                                              added_text=added_text)
