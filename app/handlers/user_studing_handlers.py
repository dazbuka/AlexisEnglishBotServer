import random
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from config import logger
from app.utils.admin_utils import count_user_tasks_by_tg_id
import app.utils.user_utils as uut
import app.database.requests as rq
import app.keyboards.user_keyboards as ukb
import data.user_messages as umsg
import data.common_messages as cmsg
from aiogram.fsm.state import StatesGroup, State
from app.utils.admin_utils import message_answer


user_studying_router = Router()


# хендлер перехода в режим изучения - первый пункт главного меню
@user_studying_router.callback_query(F.data.startswith(cmsg.COMMON_BUTTON_CHECK_TASKS))
async def check_user_tasks(call: CallbackQuery, state: FSMContext):
    # сообщение логгеру
    logger.info(f'{call.from_user.username} ({call.from_user.first_name})'
                f' - вход в меню study по *{call.data}*')
    # очищаем стейт
    await state.clear()
    # подсчитываем задания
    tasks_counter = await count_user_tasks_by_tg_id(user_tg_id=call.from_user.id)
    daily_count = tasks_counter['daily']
    missed_count = tasks_counter['missed']
    # клавиатура для дальнейшего вывода
    reply_kb = await ukb.inline_studing_menu(daily_tasks=daily_count,
                                             missed_tasks=missed_count)
    # если есть невыполненные задания сегодня или пропущенные, показываем клавиатуру
    if daily_count+missed_count != 0:
        task_message = cmsg.YOU_HAVE_TASKS.format(daily_count+missed_count)
        await message_answer(source=call, message_text=task_message, reply_markup=reply_kb)
    # если нет - все сделано и в главное меню
    else:
        reply_kb= await ukb.common_main_kb(user_tg_id=call.from_user.id)
        await message_answer(source=call, message_text=umsg.USER_STUDYING_ANSWER_ALL_DONE, reply_markup=reply_kb)
    await call.answer()


# класс ФСМ для взаимодействия, если задание является тестом
class TestAnswer(StatesGroup):
    test_task = State()


@user_studying_router.callback_query(F.data.startswith(umsg.USER_STUDYING_BUTTON_NEXT_DAILY_TASK))
@user_studying_router.callback_query(F.data.startswith(umsg.USER_STUDYING_BUTTON_NEXT_MISSED_TASK))
async def next_task_pressed(call: CallbackQuery, state: FSMContext):
    # очищаем стейт
    await state.clear()
    task_type = ''
    # получаем список заданий для этого пользователя с атрибутом отправлено = нет, сегодня или пропущенные
    if call.data.startswith(umsg.USER_STUDYING_BUTTON_NEXT_DAILY_TASK):
        task_list = await rq.get_tasks_by_filters(user_tg_id=call.from_user.id,
                                                  sent=False,
                                                  daily_tasks_only=True)
        task_type = 'daily'
    elif call.data.startswith(umsg.USER_STUDYING_BUTTON_NEXT_MISSED_TASK):
        task_list = await rq.get_tasks_by_filters(user_tg_id=call.from_user.id,
                                                  sent=False,
                                                  missed_tasks_only=True)
        task_type = 'missed'
    # если получен пустой список заданий
    if not task_list:
        reply_kb = await ukb.common_main_kb(user_tg_id= call.from_user.id)
        message_text = umsg.USER_STUDYING_ANSWER_ALL_DONE_WITH_TYPE.format(task_type)

        await message_answer(source=call, message_text=message_text, reply_markup=reply_kb)
    # если задания есть - отправляемЮ сначала проверим тест или задание
    else:
        # выбираем рандомное из имеющихся невыполненных
        task = random.choice(task_list)
        # подсчитываем задания
        tasks_counter = await count_user_tasks_by_tg_id(user_tg_id=call.from_user.id)
        daily_count = tasks_counter['daily']
        missed_count = tasks_counter['missed']
        # если тест - запускаем фсм
        if task.media.media_type.startswith('test'):
            # формируем меню ответа (клавиатуру)

            reply_kb = await ukb.inline_studing_menu(task_id=task.id,
                                                     daily_tasks=daily_count,
                                                     missed_tasks=missed_count)
            await uut.send_test_to_user_with_kb(media=task.media, call=call, reply_kb=reply_kb)
            # запускаем фсп по вышеуказанному классу
            await state.set_state(TestAnswer.test_task)
            await state.update_data(test_task=task)
        # если не тест
        else:
            reply_kb = await ukb.inline_studing_menu(task_id=task.id,
                                                     word_id=task.media.word_id,
                                                     media_id=task.media_id,
                                                     daily_tasks=daily_count,
                                                     missed_tasks=missed_count)
            await uut.send_media_to_user_call_with_kb(media=task.media, call=call, reply_kb=reply_kb)
            await rq.update_task_status(task.id)
    # отвечаем на колбэк
    await call.answer()


# фсм, которая ждет ответ на тест, если вид задания - тест
@user_studying_router.message(F.text, TestAnswer.test_task)
async def capture_test_answer(message: Message, state: FSMContext):
    # получаем данные фсм и из нее получаем ответ, введенный пользователем
    data = await state.get_data()
    test_task = data.get('test_task')
    test_media = test_task.media
    # подсчитываем задания, формируем клавиатуру
    tasks_counter = await count_user_tasks_by_tg_id(user_tg_id=message.from_user.id)
    daily_count = tasks_counter['daily']
    missed_count = tasks_counter['missed']
    reply_kb = await ukb.inline_studing_menu(word_id=test_media.word_id,
                                             media_id=test_media.id,
                                             daily_tasks=daily_count,
                                             missed_tasks=missed_count)
    # запускаем функцию проверки ответа, передаем весь мессаж, что ответить на него внутри функции
    await uut.check_user_test_answer(media=test_media, message=message, reply_kb=reply_kb)
    # меняем статус задания на исполнено
    await rq.update_task_status(test_task.id)
    # очищаем стейт
    await state.clear()


