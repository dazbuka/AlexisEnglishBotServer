from aiogram.types import InlineKeyboardButton
from app.common_settings import *

button_next_task = InlineKeyboardButton(text=BTEXT_NEXT_TASK, callback_data=CALL_NEXT_TASK)
button_repeat_today = InlineKeyboardButton(text=BTEXT_REPEAT, callback_data=CALL_REPEAT)
button_repeat_tomorrow = InlineKeyboardButton(text=BTEXT_REPEAT_TOMORROW, callback_data=CALL_REPEAT_TOMORROW)
button_translation = InlineKeyboardButton(text=BTEXT_TRANSLATION, callback_data=CALL_TRANSLATION)
button_definition = InlineKeyboardButton(text=BTEXT_DEFINITION, callback_data=CALL_DEFINITION)
button_confirm = InlineKeyboardButton(text=BTEXT_CONFIRM, callback_data=CALL_CONFIRM)


# button to go to main menu
button_main_menu = InlineKeyboardButton(text=BTEXT_MAIN_MENU, callback_data=CALL_MAIN_MENU)
button_main_menu_back = InlineKeyboardButton(text=BTEXT_MAIN_MENU_BACK, callback_data=CALL_MAIN_MENU)

# main menu
button_quick_menu = InlineKeyboardButton(text=BTEXT_TASKS_MENU, callback_data=CALL_TASKS_MENU)

button_revision_menu = InlineKeyboardButton(text=BTEXT_REVISION_MENU, callback_data=CALL_REVISION_MENU)
button_revision_menu_back = InlineKeyboardButton(text=BTEXT_REVISION_MENU_BACK, callback_data=CALL_REVISION_MENU)

button_revision_sources = InlineKeyboardButton(text=BTEXT_REVISION_SOURCES_MENU, callback_data=CALL_REVISION_SOURCES)

button_revision_words_menu = InlineKeyboardButton(text=BTEXT_REVISION_WORDS_MENU, callback_data=CALL_REVISION_WORDS)
button_revision_words_menu_back = InlineKeyboardButton(text=BTEXT_REVISION_WORDS_MENU_BACK, callback_data=CALL_REVISION_WORDS)

button_revision_colls_menu = InlineKeyboardButton(text=BTEXT_REVISION_COLLS_MENU, callback_data=CALL_REVISION_COLLS)
button_revision_colls_menu_back = InlineKeyboardButton(text=BTEXT_REVISION_COLLS_MENU_BACK, callback_data=CALL_REVISION_COLLS)


button_links_menu = InlineKeyboardButton(text=BTEXT_LINKS_MENU, callback_data=CALL_LINKS_MENU)
button_links_menu_back = InlineKeyboardButton(text=BTEXT_LINKS_MENU_BACK, callback_data=CALL_LINKS_MENU)

button_homework_menu = InlineKeyboardButton(text=BTEXT_HOMEWORK_MENU, callback_data=CALL_SHOW_HOMEWORK)
button_homework_menu_back = InlineKeyboardButton(text=BTEXT_HOMEWORK_MENU_BACK, callback_data=CALL_SHOW_HOMEWORK)

button_config_menu = InlineKeyboardButton(text=BTEXT_CONFIG_MENU, callback_data=CALL_CONFIG_MENU)
button_config_menu_back = InlineKeyboardButton(text=BTEXT_CONFIG_MENU_BACK, callback_data=CALL_CONFIG_MENU)

button_config_sending_time = InlineKeyboardButton(text=BTEXT_CONFIG_SENDING_TIME, callback_data=CALL_CONFIG_SENDING_TIME)

button_admin_menu = InlineKeyboardButton(text=BTEXT_ADMIN_MENU, callback_data=CALL_ADMIN_MENU)
button_admin_menu_back = InlineKeyboardButton(text=BTEXT_ADMIN_MENU_BACK, callback_data=CALL_ADMIN_MENU)


button_adding_menu = InlineKeyboardButton(text=BTEXT_ADDING_MENU, callback_data=CALL_ADDING_MENU)
button_adding_menu_back = InlineKeyboardButton(text=BTEXT_ADDING_MENU_BACK, callback_data=CALL_ADDING_MENU)

button_add_source = InlineKeyboardButton(text=BTEXT_ADD_SOURCE, callback_data=CALL_ADD_SOURCE)
button_add_word = InlineKeyboardButton(text=BTEXT_ADD_WORD, callback_data=CALL_ADD_WORD)
button_add_coll = InlineKeyboardButton(text=BTEXT_ADD_COLL, callback_data=CALL_ADD_COLL)
button_add_test = InlineKeyboardButton(text=BTEXT_ADD_TEST, callback_data=CALL_ADD_TEST)
button_add_group = InlineKeyboardButton(text=BTEXT_ADD_GROUP, callback_data=CALL_ADD_GROUP)
button_add_homework = InlineKeyboardButton(text=BTEXT_ADD_HOMEWORK, callback_data=CALL_ADD_HOMEWORK)
button_add_link = InlineKeyboardButton(text=BTEXT_ADD_LINK, callback_data=CALL_ADD_LINK)


button_setting_menu = InlineKeyboardButton(text=BTEXT_SETTING_MENU, callback_data=CALL_SETTING_MENU)
button_setting_menu_back = InlineKeyboardButton(text=BTEXT_SETTING_MENU_BACK, callback_data=CALL_SETTING_MENU)

button_set_scheme = InlineKeyboardButton(text=BTEXT_SET_SCHEME, callback_data=CALL_SET_SCHEME)
button_set_coll = InlineKeyboardButton(text=BTEXT_SET_COLL, callback_data=CALL_SET_COLL)

button_editing_menu = InlineKeyboardButton(text=BTEXT_EDITING_MENU, callback_data=CALL_EDITING_MENU)
button_editing_menu_back = InlineKeyboardButton(text=BTEXT_EDITING_MENU_BACK, callback_data=CALL_EDITING_MENU)

button_deleting_menu = InlineKeyboardButton(text=BTEXT_DELETING_MENU, callback_data=CALL_DELETING_MENU)
button_deleting_menu_back = InlineKeyboardButton(text=BTEXT_DELETING_MENU_BACK, callback_data=CALL_DELETING_MENU)

button_delete_task = InlineKeyboardButton(text=BTEXT_DELETE_TASK, callback_data=CALL_DELETE_TASK)

button_update_user_intervals = InlineKeyboardButton(text=BTEXT_UPDATE_USER_INTERVALS, callback_data=CALL_UPDATE_USER_INTERVALS)
button_delete_test_media = InlineKeyboardButton(text=BTEXT_DELETE_TEST_MEDIA, callback_data=CALL_DELETE_TEST_MEDIA)

button_edit_source = InlineKeyboardButton(text=BTEXT_EDIT_SOURCE, callback_data=CALL_EDIT_SOURCE)
button_edit_word = InlineKeyboardButton(text=BTEXT_EDIT_WORD, callback_data=CALL_EDIT_WORD)
button_edit_coll = InlineKeyboardButton(text=BTEXT_EDIT_COLL, callback_data=CALL_EDIT_COLL)
button_edit_link = InlineKeyboardButton(text=BTEXT_EDIT_LINK, callback_data=CALL_EDIT_LINK)
button_edit_group = InlineKeyboardButton(text=BTEXT_EDIT_GROUP, callback_data=CALL_EDIT_GROUP)
button_edit_homework = InlineKeyboardButton(text=BTEXT_EDIT_HOMEWORK, callback_data=CALL_EDIT_HOMEWORK)


# changing buttons
#     inputing
button_change_source_name = InlineKeyboardButton(text=BTEXT_CHANGE_SOURCE_NAME, callback_data=CALL_CHANGING_SOURCE_NAME)
button_change_word = InlineKeyboardButton(text=BTEXT_CHANGE_WORD, callback_data=CALL_CHANGING_WORD)
button_change_group = InlineKeyboardButton(text=BTEXT_CHANGE_GROUP, callback_data=CALL_CHANGING_GROUP)
button_change_collocation = InlineKeyboardButton(text=BTEXT_CHANGE_COLL, callback_data=CALL_CHANGING_COLL)
button_change_link_name = InlineKeyboardButton(text=BTEXT_CHANGE_LINK_NAME, callback_data=CALL_CHANGING_LINK_NAME)
button_change_link_url = InlineKeyboardButton(text=BTEXT_CHANGE_LINK_URL, callback_data=CALL_CHANGING_LINK_URL)
button_change_homework = InlineKeyboardButton(text=BTEXT_CHANGE_HOMEWORK, callback_data=CALL_CHANGING_HOMEWORK)
button_change_definition = InlineKeyboardButton(text=BTEXT_CHANGE_DEFINITION, callback_data=CALL_CHANGING_DEFINITION)
button_change_translation = InlineKeyboardButton(text=BTEXT_CHANGE_TRANSLATION, callback_data=CALL_CHANGING_TRANSLATION)
button_change_media = InlineKeyboardButton(text=BTEXT_CHANGE_MEDIA, callback_data=CALL_CHANGING_MEDIA)
button_change_caption = InlineKeyboardButton(text=BTEXT_CHANGE_CAPTION, callback_data=CALL_CHANGING_CAPTION)
#     capturing

button_change_sources = InlineKeyboardButton(text=BTEXT_CHANGE_SOURCES, callback_data=CALL_CHANGING_SOURCES)
button_change_words = InlineKeyboardButton(text=BTEXT_CHANGE_WORDS, callback_data=CALL_CHANGING_WORDS)
button_change_groups = InlineKeyboardButton(text=BTEXT_CHANGE_GROUPS, callback_data=CALL_CHANGING_GROUPS)
button_change_collocations = InlineKeyboardButton(text=BTEXT_CHANGE_COLLS, callback_data=CALL_CHANGING_COLLS)
button_change_users = InlineKeyboardButton(text=BTEXT_CHANGE_USERS, callback_data=CALL_CHANGING_USERS)
button_change_colls = InlineKeyboardButton(text=BTEXT_CHANGE_COLLS, callback_data=CALL_CHANGING_COLLS)
button_change_dates = InlineKeyboardButton(text=BTEXT_CHANGE_DATES, callback_data=CALL_CHANGING_DATES)
button_change_priority = InlineKeyboardButton(text=BTEXT_CHANGE_PRIRITY, callback_data=CALL_CHANGING_PRIRITY)
button_change_days = InlineKeyboardButton(text=BTEXT_CHANGE_DAYS, callback_data=CALL_CHANGING_DAYS)
button_change_parts = InlineKeyboardButton(text=BTEXT_CHANGE_PARTS, callback_data=CALL_CHANGING_PARTS)
button_change_levels = InlineKeyboardButton(text=BTEXT_CHANGE_LEVELS, callback_data=CALL_CHANGING_LEVELS)



















