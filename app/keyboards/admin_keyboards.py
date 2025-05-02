from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import data.admin_messages as amsg
import data.common_messages as cmsg
import app.database.requests as rq
import app.handlers.callback_messages as callmsg
from datetime import date, timedelta


# inline клавиатура main
async def main_admin_menu_kb():
    inline_keyboard = [
        [
            InlineKeyboardButton(text=amsg.ADMIN_BUTTON_ADDING_MENU, callback_data=amsg.ADMIN_BUTTON_ADDING_MENU)
        ],
        [
            InlineKeyboardButton(text=amsg.ADMIN_BUTTON_WORK_WITH_DB, callback_data=amsg.ADMIN_BUTTON_WORK_WITH_DB)
        ],
        [
            InlineKeyboardButton(text=cmsg.COMMON_BUTTON_MAIN_MENU, callback_data=callmsg.CALL_PRESS_MAIN_MENU)
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

# инлайн меню для заблокированного пользователя
async def admin_block_menu(user_tg_id):
    inline_keyboard = [
        [
            InlineKeyboardButton(text=amsg.ADMIN_BUTTON_UNBLOCK_USER,
                                 callback_data=f'{amsg.ADMIN_BUTTON_UNBLOCK_USER}{user_tg_id}')
        ],
        [
            InlineKeyboardButton(text=amsg.ADMIN_BUTTON_DELETE_USER,
                                 callback_data=f'{amsg.ADMIN_BUTTON_DELETE_USER}{user_tg_id}')
        ]
        ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# inline клавиатура main adding
async def admin_adding_menu_kb():
    inline_keyboard = [
        [
            InlineKeyboardButton(text=amsg.ADMIN_BUTTON_ADD_WORD, callback_data=amsg.ADMIN_BUTTON_ADD_WORD)
        ],
        [
            InlineKeyboardButton(text=amsg.ADMIN_BUTTON_ADD_MEDIA, callback_data=amsg.ADMIN_BUTTON_ADD_MEDIA)
        ],
        [
            InlineKeyboardButton(text=amsg.ADMIN_BUTTON_ADD_TEST, callback_data=amsg.ADMIN_BUTTON_ADD_TEST)
        ],
        [
            InlineKeyboardButton(text=amsg.ADMIN_BUTTON_ADD_HOMEWORK, callback_data=amsg.ADMIN_BUTTON_ADD_HOMEWORK)
        ],
        [
            InlineKeyboardButton(text=amsg.ADMIN_BUTTON_ADD_TASK, callback_data=amsg.ADMIN_BUTTON_ADD_TASK)
        ],
        [
            InlineKeyboardButton(text=amsg.ADMIN_BUTTON_MAIN_ADMIN_MENU,
                                 callback_data=amsg.ADMIN_BUTTON_MAIN_ADMIN_MENU),
            InlineKeyboardButton(text=amsg.ADMIN_BUTTON_MAIN_MENU,
                                 callback_data=callmsg.CALL_PRESS_MAIN_MENU),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# inline клавиатура main adding
async def admin_adding_task_menu_kb():
    inline_keyboard = [
        [
            InlineKeyboardButton(text=amsg.ADMIN_BUTTON_ADD_TASK_SHEMA, callback_data=amsg.ADMIN_BUTTON_ADD_TASK_SHEMA)
        ],
        [
            InlineKeyboardButton(text=amsg.ADMIN_BUTTON_ADD_TASK_MEDIA, callback_data=amsg.ADMIN_BUTTON_ADD_TASK_MEDIA)
        ],
        [
            InlineKeyboardButton(text=amsg.ADMIN_BUTTON_MAIN_ADMIN_MENU,
                                 callback_data=amsg.ADMIN_BUTTON_MAIN_ADMIN_MENU),
            InlineKeyboardButton(text=amsg.ADMIN_BUTTON_MAIN_MENU,
                                 callback_data=callmsg.CALL_PRESS_MAIN_MENU),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# inline keyboard adding word
async def admin_adding_word_kb(adding_level : bool = False,
                               adding_part : bool = False,
                               confirmation : bool = False):
    builder = InlineKeyboardBuilder()

    if adding_level:
        for level in cmsg.COMMON_LIST_STUDY_LEVELS:
            builder.button(text=f'-{level}-', callback_data=f'{callmsg.CALL_ADM_ADD_WORD_LEVEL}{level}')

    if adding_part:
        for part in cmsg.COMMON_LIST_PARTS_OF_SPEECH:
            builder.button(text=f'-{part}-', callback_data=f'{callmsg.CALL_ADM_ADD_WORD_PART}{part}')

    if confirmation:
        builder.button(text=amsg.ADMIN_BUTTON_CONFIRM_DATA,
                       callback_data=callmsg.CALL_ADM_ADD_WORD_CONF + cmsg.YES)
        builder.button(text=amsg.ADMIN_BUTTON_NO_CONFIRM_DATA,
                       callback_data=callmsg.CALL_ADM_ADD_WORD_CONF + cmsg.NO)
        builder.button(text='in devops', callback_data='no call dev')

    builder.button(text=amsg.ADMIN_BUTTON_ADDING_MENU, callback_data=amsg.ADMIN_BUTTON_ADDING_MENU)
    builder.button(text=amsg.ADMIN_BUTTON_MAIN_ADMIN_MENU, callback_data=amsg.ADMIN_BUTTON_MAIN_ADMIN_MENU)
    builder.button(text=amsg.ADMIN_BUTTON_MAIN_MENU, callback_data=callmsg.CALL_PRESS_MAIN_MENU)
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True)


# inline keyboard adding media
async def admin_adding_media_kb(adding_word_list : list = None,
                                adding_level : bool = False,
                                adding_study_day : list = None,
                                confirmation : bool = False):
    builder = InlineKeyboardBuilder()

    if adding_word_list:
        for word in adding_word_list:
            builder.button(text=f'{word}', callback_data=f'{callmsg.CALL_ADM_ADD_MEDIA_WORD}{word[:15]}')

    if adding_level:
        for level in cmsg.COMMON_LIST_STUDY_LEVELS:
            builder.button(text=f'-{level}-', callback_data=f'{callmsg.CALL_ADM_ADD_MEDIA_LEVEL}{level}')

    if adding_study_day:
        for day in adding_study_day:
            builder.button(text=f'{day}', callback_data=f'{callmsg.CALL_ADM_ADD_MEDIA_DAY}{day}')


    if confirmation:
        builder.button(text=amsg.ADMIN_BUTTON_CONFIRM_DATA,
                       callback_data=callmsg.CALL_ADM_ADD_MEDIA_CONF + cmsg.YES)
        builder.button(text=amsg.ADMIN_BUTTON_NO_CONFIRM_DATA,
                       callback_data=callmsg.CALL_ADM_ADD_MEDIA_CONF + cmsg.NO)
        builder.button(text='in devops', callback_data='no call dev')


    builder.button(text=amsg.ADMIN_BUTTON_ADDING_MENU, callback_data=amsg.ADMIN_BUTTON_ADDING_MENU)
    builder.button(text=amsg.ADMIN_BUTTON_MAIN_ADMIN_MENU, callback_data=amsg.ADMIN_BUTTON_MAIN_ADMIN_MENU)
    builder.button(text=amsg.ADMIN_BUTTON_MAIN_MENU, callback_data=callmsg.CALL_PRESS_MAIN_MENU)
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True)


# inline keyboard adding test
async def admin_adding_test_kb(adding_word_list : list = None,
                               adding_test_type_list : list = None,
                               adding_study_day : list = None,
                               confirmation : bool = False):
    builder = InlineKeyboardBuilder()

    if adding_word_list:
        for word in adding_word_list:
            builder.button(text=f'-{word}-', callback_data=f'{callmsg.CALL_ADM_ADD_TEST_WORD}{word[:15]}')

    if adding_test_type_list:
        for test_type in adding_test_type_list:
            builder.button(text=f'{test_type}',
                           callback_data=f'{callmsg.CALL_ADM_ADD_TEST_TYPE}{test_type}')

    if adding_study_day:
        for day in adding_study_day:
            builder.button(text=f'{day}', callback_data=f'{callmsg.CALL_ADM_ADD_TEST_DAY}{day}')

    if confirmation:
        builder.button(text=amsg.ADMIN_BUTTON_CONFIRM_DATA,
                       callback_data=callmsg.CALL_ADM_ADD_TEST_CONF + cmsg.YES)
        builder.button(text=amsg.ADMIN_BUTTON_NO_CONFIRM_DATA,
                       callback_data=callmsg.CALL_ADM_ADD_TEST_CONF + cmsg.NO)
        builder.button(text='in devops', callback_data='no call dev')

    builder.button(text=amsg.ADMIN_BUTTON_ADDING_MENU, callback_data=amsg.ADMIN_BUTTON_ADDING_MENU)
    builder.button(text=amsg.ADMIN_BUTTON_MAIN_ADMIN_MENU, callback_data=amsg.ADMIN_BUTTON_MAIN_ADMIN_MENU)
    builder.button(text=amsg.ADMIN_BUTTON_MAIN_MENU, callback_data=callmsg.CALL_PRESS_MAIN_MENU)
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True)


# inline keyboard adding task
async def admin_adding_task_kb(adding_word_list : list = None,
                               adding_media_list: list = None,
                               adding_user_list : list = None,
                               adding_study_day : bool = False,
                               confirmation : bool = False):
    builder = InlineKeyboardBuilder()

    if adding_word_list:
        for word in adding_word_list:
            builder.button(text=f'{word}', callback_data=f'{callmsg.CALL_ADM_ADD_TASK_WORD}{word[:15]}')
        builder.button(text=amsg.ADM_CONFIRM,
                       callback_data=f'{callmsg.CALL_ADM_ADD_TASK_WORD}{callmsg.CALL_ADMIN_END_CHOOSING}')

    if adding_media_list:
        for media in adding_media_list:
            builder.button(text=f'{media}',
                           callback_data=f'{callmsg.CALL_ADM_ADD_TASK_MEDIA}{media[:15]}')
        builder.button(text=amsg.ADM_CONFIRM,
                       callback_data=f'{callmsg.CALL_ADM_ADD_TASK_MEDIA}{callmsg.CALL_ADMIN_END_CHOOSING}')

    if adding_user_list:
        for user in adding_user_list:
            builder.button(text=f'{user}', callback_data=f'{callmsg.CALL_ADM_ADD_TASK_USER}{user[:15]}')
        builder.button(text=amsg.ADM_CONFIRM,
                       callback_data=f'{callmsg.CALL_ADM_ADD_TASK_USER}{callmsg.CALL_ADMIN_END_CHOOSING}')

    if adding_study_day:
        for i in range(12):
            day = (date.today() + timedelta(days=i)).strftime("%d.%m.%Y")
            builder.button(text=f'-{day}-', callback_data=f'{callmsg.CALL_ADM_ADD_TASK_DAY}{day}')


    if confirmation:
        builder.button(text=amsg.ADMIN_BUTTON_CONFIRM_DATA,
                       callback_data=callmsg.CALL_ADM_ADD_TASK_CONF + cmsg.YES)
        builder.button(text=amsg.ADMIN_BUTTON_NO_CONFIRM_DATA,
                       callback_data=callmsg.CALL_ADM_ADD_TASK_CONF + cmsg.NO)
        builder.button(text='in devops', callback_data='no call dev')

    builder.button(text=amsg.ADMIN_BUTTON_ADDING_MENU, callback_data=amsg.ADMIN_BUTTON_ADDING_MENU)
    builder.button(text=amsg.ADMIN_BUTTON_MAIN_ADMIN_MENU, callback_data=amsg.ADMIN_BUTTON_MAIN_ADMIN_MENU)
    builder.button(text=amsg.ADMIN_BUTTON_MAIN_MENU, callback_data=callmsg.CALL_PRESS_MAIN_MENU)
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True)


# inline keyboard adding homework
async def admin_adding_homework_kb(adding_user_list : list = None,
                               adding_study_day : bool = False,
                               confirmation : bool = False):
    builder = InlineKeyboardBuilder()

    if adding_user_list:
        for user in adding_user_list:
            builder.button(text=f'{user}', callback_data=f'{callmsg.CALL_ADM_ADD_HOME_USER}{user[:15]}')
        builder.button(text=amsg.ADM_CONFIRM,
                       callback_data=f'{callmsg.CALL_ADM_ADD_HOME_USER}{callmsg.CALL_ADMIN_END_CHOOSING}')

    if adding_study_day:
        for i in range(12):
            day = (date.today() + timedelta(days=i)).strftime("%d.%m.%Y")
            builder.button(text=f'-{day}-', callback_data=f'{callmsg.CALL_ADM_ADD_HOME_DAY}{day}')


    if confirmation:
        builder.button(text=amsg.ADMIN_BUTTON_CONFIRM_DATA,
                       callback_data=callmsg.CALL_ADM_ADD_HOME_CONF + cmsg.YES)
        builder.button(text=amsg.ADMIN_BUTTON_NO_CONFIRM_DATA,
                       callback_data=callmsg.CALL_ADM_ADD_HOME_CONF + cmsg.NO)
        builder.button(text='in devops', callback_data='no call dev')


    builder.button(text=amsg.ADMIN_BUTTON_ADDING_MENU, callback_data=amsg.ADMIN_BUTTON_ADDING_MENU)
    builder.button(text=amsg.ADMIN_BUTTON_MAIN_ADMIN_MENU, callback_data=amsg.ADMIN_BUTTON_MAIN_ADMIN_MENU)
    builder.button(text=amsg.ADMIN_BUTTON_MAIN_MENU, callback_data=callmsg.CALL_PRESS_MAIN_MENU)
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True)