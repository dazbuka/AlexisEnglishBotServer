from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove
)

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from config import ADMIN_IDS

import app.database.requests as rq
import data.user_messages as umsg
import data.common_messages as cmsg
import data.admin_messages as amsg
import app.handlers.callback_messages as callmsg
from app.utils.admin_utils import count_user_tasks_by_tg_id

# общая главная клавиатура
async def common_main_kb(user_tg_id):
    # подсчитываем задания, формируем клавиатуру
    tasks_counter = await count_user_tasks_by_tg_id(user_tg_id=user_tg_id)
    daily_count = tasks_counter['daily']
    missed_count = tasks_counter['missed']
    # создаем список кнопок для клавиатуры, используем количество неисполненных заданий
    if daily_count+missed_count != 0:
        # добавка к тексту кнопки фразу у вас х заданий
        task_message = cmsg.HAVE_TASKS.format(daily_count + missed_count)
    else:
        # добавка к тексту кнопки фразы, что заданий нет
        task_message = cmsg.HAVE_NO_TASKS
    # общая часть клавиатуры
    inline_keyboard = [
        [InlineKeyboardButton(text=f'{cmsg.COMMON_BUTTON_CHECK_TASKS} {task_message}',
                              callback_data=cmsg.COMMON_BUTTON_CHECK_TASKS),
        InlineKeyboardButton(text=cmsg.COMMON_BUTTON_REVISION,
                              callback_data=cmsg.COMMON_BUTTON_REVISION)],
        [InlineKeyboardButton(text=cmsg.COMMON_BUTTON_HOMEWORK,
                              callback_data=cmsg.COMMON_BUTTON_HOMEWORK),
        InlineKeyboardButton(text=cmsg.COMMON_BUTTON_SETTINGS,
                              callback_data=cmsg.COMMON_BUTTON_SETTINGS)]
    ]
    # админская добавка
    inline_keyboard_admin = [
        [InlineKeyboardButton(text=amsg.ADMIN_BUTTON_MAIN_ADMIN_MENU,
                              callback_data=amsg.ADMIN_BUTTON_MAIN_ADMIN_MENU)]
    ]
    # админка, если телеграм ИД находится в списке админов
    if user_tg_id in ADMIN_IDS:
        inline_keyboard.extend(inline_keyboard_admin)
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# инлайн меню для заблокированного пользователя
async def inline_block_menu():
    inline_keyboard = [[
            InlineKeyboardButton(text=umsg.USER_MSG_REQUEST_WHEN_BLOCKED,
                                 callback_data=umsg.USER_MSG_REQUEST_WHEN_BLOCKED)
        ]]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# меню процесс обучения
async def inline_studing_menu(task_id: int = 1,
                              word_id: int = 1,
                              media_id: int = 0,
                              daily_tasks: int = 0,
                              missed_tasks: int = 0):
    # если аргументы слово и медиа непустые - тогда меню дополняется переводом и добавлением в таски
    if word_id != 0 and media_id != 0:
        inline_keyboard = [
            [
                InlineKeyboardButton(text=umsg.USER_BUTTON_DEFINITION,
                                     callback_data=umsg.USER_BUTTON_DEFINITION + str(word_id)),
                InlineKeyboardButton(text=umsg.USER_BUTTON_TRANSLATION,
                                     callback_data=umsg.USER_BUTTON_TRANSLATION + str(word_id))
            ],
            [
                InlineKeyboardButton(text=umsg.USER_BUTTON_REPEAT_TODAY,
                                     callback_data=umsg.USER_BUTTON_REPEAT_TODAY + str(media_id)),
                InlineKeyboardButton(text=umsg.USER_BUTTON_REPEAT_TOMORROW,
                                     callback_data=umsg.USER_BUTTON_REPEAT_TOMORROW + str(media_id))
            ]
            ]
    else:
        inline_keyboard = []
    # эта часть клавиатуры будет в любом случае
    inline_keyboard_next =    (
        [
            InlineKeyboardButton(text=umsg.USER_STUDYING_BUTTON_NEXT_DAILY_TASK + ' (' + str(daily_tasks) + ')',
                                 callback_data=umsg.USER_STUDYING_BUTTON_NEXT_DAILY_TASK + str(task_id)),
            InlineKeyboardButton(text=umsg.USER_STUDYING_BUTTON_NEXT_MISSED_TASK + ' (' + str(missed_tasks) + ')',
                                 callback_data=umsg.USER_STUDYING_BUTTON_NEXT_MISSED_TASK + str(task_id))
        ],
        [
            InlineKeyboardButton(text=cmsg.PRESS_MAIN_MENU, callback_data=callmsg.CALL_PRESS_MAIN_MENU)
        ]
    )
    # объединяем
    inline_keyboard=[*inline_keyboard, *inline_keyboard_next]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# inline клавиатура при просмотре всех заданий ревижн
async def inline_revision_tasks_menu(previous_task_id: int = 0,
                                    next_task_id: int = 0,
                                    word_id: int = 0,
                                    media_id: int = 0):
    inline_keyboard = [
        [
            InlineKeyboardButton(text=umsg.USER_BUTTON_DEFINITION,
                                 callback_data=umsg.USER_BUTTON_DEFINITION + str(word_id)),
            InlineKeyboardButton(text=umsg.USER_BUTTON_TRANSLATION,
                                 callback_data=umsg.USER_BUTTON_TRANSLATION + str(word_id))
        ],
        [
            InlineKeyboardButton(text=umsg.USER_BUTTON_REPEAT_TODAY,
                                 callback_data=umsg.USER_BUTTON_REPEAT_TODAY + str(media_id)),
            InlineKeyboardButton(text=umsg.USER_BUTTON_REPEAT_TOMORROW,
                                 callback_data=umsg.USER_BUTTON_REPEAT_TOMORROW + str(media_id))
        ],
        [
            InlineKeyboardButton(text=umsg.USER_REVISION_BUTTON_PREVIOUS_TASK,
                                 callback_data=umsg.USER_REVISION_BUTTON_SHOW_LAST_TASKS + str(previous_task_id)),
            InlineKeyboardButton(text=umsg.USER_REVISION_BUTTON_NEXT_TASK,
                                 callback_data=umsg.USER_REVISION_BUTTON_SHOW_LAST_TASKS + str(next_task_id))
        ],
        [
            InlineKeyboardButton(text=umsg.USER_BUTTON_REVISION_MENU,
                                 callback_data=cmsg.COMMON_BUTTON_REVISION),
            InlineKeyboardButton(text=umsg.USER_BUTTON_MAIN_MENU,
                                 callback_data=callmsg.CALL_PRESS_MAIN_MENU)
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# инлайн меню при ревижене
async def inline_revision_menu(next_task_id: int = 0):
    inline_keyboard = [
        [
            InlineKeyboardButton(text=umsg.USER_REVISION_BUTTON_SHOW_LAST_WORDS,
                                 callback_data=umsg.USER_REVISION_BUTTON_SHOW_LAST_WORDS)
        ],
        [
            InlineKeyboardButton(text=umsg.USER_REVISION_BUTTON_SHOW_LAST_TASKS,
                                 callback_data=umsg.USER_REVISION_BUTTON_SHOW_LAST_TASKS + str(next_task_id))
        ],
        [
            InlineKeyboardButton(text=cmsg.PRESS_MAIN_MENU, callback_data=callmsg.CALL_PRESS_MAIN_MENU)
        ]
        ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# revision words
async def inline_revision_word_buttons_kb(word_list):
    builder = InlineKeyboardBuilder()
    for word in word_list:
        builder.button(text=f'- {word} -', callback_data=f'{callmsg.CALL_REVISION_WORD}{word}')
    builder.button(text=umsg.USER_BUTTON_REVISION_MENU, callback_data=cmsg.COMMON_BUTTON_REVISION)
    builder.button(text=cmsg.PRESS_MAIN_MENU, callback_data=callmsg.CALL_PRESS_MAIN_MENU)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


# revision collocation
async def inline_revision_collocations_buttons_kb(coll_list):
    builder = InlineKeyboardBuilder()
    for colloc in coll_list:
        builder.button(text=f'- {colloc[1]} -', callback_data=f'{callmsg.CALL_REVISION_COLLOCATION}{colloc[0]}')
    builder.button(text=umsg.USER_REVISION_BUTTON_WORD_LIST, callback_data=umsg.USER_REVISION_BUTTON_SHOW_LAST_WORDS)
    builder.button(text=cmsg.PRESS_MAIN_MENU, callback_data=callmsg.CALL_PRESS_MAIN_MENU)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


# инлайн меню при ревижене
async def inline_settings_menu():
    inline_keyboard = [
        [InlineKeyboardButton(text=umsg.USER_REVISION_BUTTON_REMINDER_TIME,
                              callback_data=umsg.USER_REVISION_BUTTON_REMINDER_TIME)],
        [InlineKeyboardButton(text=cmsg.PRESS_MAIN_MENU,
                              callback_data=callmsg.CALL_PRESS_MAIN_MENU)]
        ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# settings menu
async def inline_settings_intervals_buttons_kb(interval_list):
    builder = InlineKeyboardBuilder()
    for interval in interval_list:
        builder.button(text=f'{interval}', callback_data=f'{callmsg.CALL_SETTINGS_INTERVAL}{interval}')
    builder.button(text=umsg.USER_BUTTON_CONFIRM, callback_data=f'{callmsg.CALL_SETTINGS_INTERVAL}{callmsg.CALL_USER_END_CHOOSING}')
    builder.button(text=cmsg.COMMON_BUTTON_SETTINGS, callback_data=cmsg.COMMON_BUTTON_SETTINGS)
    builder.button(text=cmsg.PRESS_MAIN_MENU, callback_data=callmsg.CALL_PRESS_MAIN_MENU)
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True)