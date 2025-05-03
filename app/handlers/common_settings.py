# v🔁⬆️🛠️♟️🧑‍🏫🖊️🗓️📑📬🧰🗃️⚙️📲🕹🔎📚👇📌📖➡️⬅️🗄⚙️🌏

from enum import Enum

class MediaType(Enum):
    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    LOCATION = "location"
    CONTACT = "contact"
    STICKER = "sticker"
    ANIMATION = "animation"

class CarouselButtons(Enum):
    NEXT = '➡️'
    LAST = '⏭️'
    PREV = '⬅️'
    FIRST = '⏮️'


# TEXT_NEXT = '➡️'
# TEXT_LAST = '⏭️'
# TEXT_PREV = '⬅️'
# TEXT_FIRST = '⏮️'
# #
# CALL_NEXT = '>>_'
# CALL_LAST = '>|_'
# CALL_PREV = '<<_'
# CALL_FIRST = '|<_'


# из конфиг
REMINDER_INTERVAL='09:00 - 22:00' # время работы напоминатора
REMINDER_SLEEP_INTERVAL=60*60 # промежутки между запусками функции напоминатора
SENDING_SLEEP_INTERVAL=1 #интервалы между отправкой сообщений пользователям

COUNT_OF_DELETED_MESSAGES = 15
COUNT_OF_LAST_WORDS_ADDING_MEDIA=10

STUDYING_DAY_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 21, 28, 35]
TEST_TYPES = ['test4','test7']


MESS_USER_ALL_DONE= '💪Stellar job, no more tasks!'






MESS_INVITE_PRESS_ANY= "🕹Press any button👇"

BTEXT_SHOW_HOMEWORK = '🏠Homework🏠'
CALL_SHOW_HOMEWORK = 'c_show_homework'
MESS_YOUR_HOMEWORK='Your homework:'
MESS_YOUR_HOMEWORK_EMPTY='🤷No homework🤷'
# menu motion
ADMIN_BUTTON_MAIN_MENU="⬆️Main menu⬆️"
ADMIN_BUTTON_MAIN_ADMIN_MENU='🛠️Admin menu🛠️'
ADMIN_BUTTON_BACK_TO_MAIN_ADMIN_MENU='⬆️Admin menu⬆️'

# maim admin menu
ADMIN_BUTTON_ADDING_MENU= '✍️Adding menu✍️'
ADMIN_BUTTON_WORK_WITH_DB= '🗄Work with DB🗄'


ADMIN_BUTTON_UNBLOCK_USER = 'Разблокировать️'
ADMIN_BUTTON_DELETE_USER = 'Удалить️'

# adding buttons
ADMIN_BUTTON_ADD_WORD= '🔤Добавить слово'
ADMIN_BUTTON_ADD_MEDIA= '🏞️Добавить media'
ADMIN_BUTTON_ADD_TEST= '❓Добавить тест'
ADMIN_BUTTON_ADD_HOMEWORK= '🏠Добавить домашнее задание'
ADMIN_BUTTON_ADD_TASK= '📌Назначить задание'
ADMIN_BUTTON_ADD_TASK_SHEMA= '📌Назначить задание по схеме'
ADMIN_BUTTON_ADD_TASK_BY_SHEMA= '📌Назначить задание по схеме2'
ADMIN_BUTTON_ADD_TASK_MEDIA= '📌Назначить задание медиа(тест)'
ADMIN_BUTTON_ADD_GROUP= '👯️Создать группу пользователей'
# confirmation
ADMIN_BUTTON_CONFIRM_DATA="✅Все верно"
ADMIN_BUTTON_NO_CONFIRM_DATA="❌Сначала"

# adding menu welcomes
ADMIN_ADDING_MENU_WELCOME='Welcome to admin adding menu!'

# adding test

ADM_ADD_TEST_TEST = 'Выберите слово или введите его c клавиатуры:'
ADM_ADD_TEST_WORD_NOT_FIND = 'Слово не найдено, введите часть или выберите из найденных:'
ADM_ADD_TEST_DAY =  ('Выберите день изучения (или введите с клавиатуры) '
                      'с учетом уже имеющихся в стандартной схеме изучения:')
ADM_ADD_TEST_DAY_REP =  ('Выберите день изучения (или введите с клавиатуры ЦИФРУ) '
                         'с учетом уже имеющихся в стандартной схеме изучения:')
ADM_ADD_TEST_TYPE = 'Выберите тип теста'
ADM_ADD_TEST_TYPE_REP = 'Печатать не нужно. Пожалуйста, подтвердите или отмените:'
ADM_ADD_TEST_CONFIRMATION = 'Проверьте и подтвердите запись в базу данных:'
ADM_ADD_TEST_CONFIRMATION_REP = 'Печатать не нужно. Пожалуйста, подтвердите или отмените:'
ADM_ADD_TEST_ERROR = 'Ошибка при записи в базу данных, обратитесь к администратору'
ADM_ADD_TEST_ADDED = 'Тест для слова {} (тип {}) добавлено в базу данных.'
ADM_ADD_TEST_WORD_AGAIN = 'Создаем тест заново, выбирайте слово или напечатайте его или его часть:'

ADM_CONFIRM='✅CONFIRM✅'



BTEXT_DEFINITION= "🪄Definition"
CALL_DEFINITION= "@definition_"
BTEXT_TRANSLATION= "📗Translation"
CALL_TRANSLATION= "@translation_"
BTEXT_REPEAT="🔁Repeat later"
CALL_REPEAT= "@repeat_today_"
BTEXT_NEXT_TASK= "➡️Next"
CALL_NEXT_TASK= "@next_"
BTEXT_REPEAT_TOMORROW= "🔄Repeat tomorrow"
CALL_REPEAT_TOMORROW= "@repeat_tomorrow_"





YES='yes'
NO='no'


HAVE_TASKS = "({})"
HAVE_NO_TASKS = "(-)"

USER_MSG_WHEN_BLOCKED='Access denied.'
USER_MSG_WHEN_WAITING="Access denied. Wait for admin's permission."
USER_MSG_WHEN_DELETED='Request declined. Access denied.'
USER_MSG_REQUEST_WHEN_BLOCKED="Send request to admin."
USER_MSG_REQUEST_SENDED="Request sended."
# menu moving
USER_BUTTON_MAIN_MENU = '⬆️Main menu⬆️'
USER_BUTTON_REVISION_MENU = '🔎Revision menu🔎'

# user inviting
USER_INVITE_PRESS_ANY_BUTTON= "🕹Press any button👇"
USER_INVITE_CHOOSE_AND_PRESS_ANY= "📌Choose any and tap it👇"

#studing menu
USER_STUDYING_BUTTON_NEXT_DAILY_TASK= "📬Next daily"
USER_STUDYING_BUTTON_NEXT_MISSED_TASK= "🧰Next missed"
# studying answers messages

USER_STUDYING_ANSWER_ALL_DONE_WITH_TYPE= '💪Stellar job, no more {} tasks!'
# test messages
USER_STUDYING_TEST4_TASK_MESSAGE= 'Fill in the gaps:'
USER_STUDYING_TEST7_TASK_MESSAGE= 'Type common collocation with the word:'
USER_STUDYING_TEST_ANSWER_RIGHT_WORD= "🎉Good job, it's the right word: <b>{}</b>, your answer was: <b>{}</b>"
USER_STUDYING_TEST_CHECK_YOURSELF= '📎Check yourself, the right answer is: \n<b>{}</b>\n\nYour answer was: \n<b>{}</b>'

#revision menu
USER_REVISION_BUTTON_SHOW_LAST_WORDS= "📚Look through words📚"
USER_REVISION_BUTTON_SHOW_LAST_TASKS= "📖Look recently learned📖"
# revision words menu
USER_REVISION_BUTTON_WORD_LIST= "📚Back to words📚"
# revision last tasks  menu
USER_REVISION_BUTTON_PREVIOUS_TASK= "⬅️Previous⬅️"
USER_REVISION_BUTTON_NEXT_TASK= "➡️Next➡️"
# revision answers
USER_REVISION_ANSWER_NO_REVISION= '🤷Nothing for revision🤷'
# revision alarm
USER_REVISION_ALARM_FIRST_TASK_OPENED= "Your first studied collocation, better press button 'Previous'"

#settings menu
USER_REVISION_BUTTON_REMINDER_TIME= "⏰Reminder time⏰"
USER_BUTTON_CONFIRM="✅Confirm✅"
USER_BUTTON_SETTINGS = '⚙️Settings menu⚙️'
USER_INVITE_INTERVALS= '🕒Pick a slot for a reminder (MSK).🕝'


# common user menu
USER_BUTTON_DEFINITION= "🪄Definition"
USER_BUTTON_TRANSLATION= "📗Translation"
USER_BUTTON_REPEAT_TODAY= "🔁Repeat today"
USER_BUTTON_REPEAT_TOMORROW= "🔄Repeat tomorrow"



USER_YOUR_HOMEWORK='Your homework:'
USER_YOUR_NO_HOMEWORK='🤷No homework🤷'




MESS_YOU_HAVE_TASKS= "🗓️A friendly reminder! You have <b>{}</b> task(s) to complete!"
MESS_PRESS_ANY_BUTTON="🕹Press any button👇"
MESS_HELP = 'Hello, this is help!🤗'
MESS_DONT_UNDERSTAND= "Can't understand you, press any button:"


CALL_MAIN_MENU= '@m_main_menu️'
MESS_MAIN_MENU = "🧑‍🏫Hi, I'm AlexisEnglishBot! Welcome to main menu."
BTEXT_MAIN_MENU = "⬆️Main menu"
BTEXT_MAIN_MENU_BACK = "⬆️Back to main menu⬆️"

CALL_TASKS_MENU= '@m_quick_menu️'
MESS_TASKS_MENU_EMPTY = "You have no tasks!"
BTEXT_TASKS_MENU= '🗓️My tasks'

CALL_REVISION_MENU= '@m_revision_menu️'
MESS_REVISION_MENU = "Welcome to revision menu!"
BTEXT_REVISION_MENU= '🔎Revision'
BTEXT_REVISION_MENU_BACK = "🔎Revision"

CALL_LINKS_MENU= '@m_links_menu️'
MESS_LINKS_MENU = "Welcome to links menu!"
MESS_LINKS_MENU_EMPTY = "You have no links!"
BTEXT_LINKS_MENU= '🌏Links'
BTEXT_LINKS_MENU_BACK = "Exit to links menu"
NUM_SHOW_LINKS_COLS = 1
NUM_SHOW_LINKS_ROWS = 7



CALL_SHOW_HOMEWORK= '@m_homework_menu️'
MESS_HOMEWORK_MENU = "Welcome to homework menu!"
BTEXT_HOMEWORK_MENU= '🏠Homework'
BTEXT_HOMEWORK_MENU_BACK = "🏠Homework"

CALL_CONFIG_MENU= '@m_config_menu️'
MESS_CONFIG_MENU = "Welcome to config menu!"
BTEXT_CONFIG_MENU= '⚙️Settings'
BTEXT_CONFIG_MENU_BACK = "⚙️Settings"

CALL_CONFIG_SENDING_TIME= '@m_config_sending_time️'
BTEXT_CONFIG_SENDING_TIME= '⏰Reminder time⏰'
MESS_CONFIG_SENDING_TIME = "🕒Pick a slot for a reminder (MSK).🕝"
NUM_CONFIG_SENDING_TIME_COLS = 4
NUM_CONFIG_SENDING_TIME_ROWS = 4
CHECK_CONFIG_SENDING_TIME = '🟣'



CALL_ADMIN_MENU= '@m_admin_menu️'
MESS_ADMIN_MENU = "Welcome to main admin menu!"
BTEXT_ADMIN_MENU= '🛠️---Admin menu NEW---🛠️'
BTEXT_ADMIN_MENU_BACK = "🛠️Admin menu"

CALL_REVISION_SOURCES= '@m_revision_sources_menu️'
MESS_REVISION_SOURCES = 'Выберите источник'
MESS_REVISION_SOURCES_MENU_EMPTY = "You have no sources!"
BTEXT_REVISION_SOURCES_MENU= '🎬Sources'
BTEXT_REVISION_SOURCES_MENU_BACK = "🎬Sources"

NUM_REVISION_SOURCES_COLS = 1
NUM_REVISION_SOURCES_ROWS = 5
CHECK_REVISION_SOURCES= '🟣'


CALL_REVISION_WORDS= '@m_revision_words_️'
MESS_REVISION_WORDS_MENU = "Choose word!"
BTEXT_REVISION_WORDS_MENU= '📚Revision words'
BTEXT_REVISION_WORDS_MENU_BACK = "📚Words"
NUM_REVISION_WORDS_COLS = 1
NUM_REVISION_WORDS_ROWS = 5
CHECK_REVISION_WORDS = '🟣'





CALL_REVISION_COLLS= '@m_revision_colls_menu️'
BTEXT_REVISION_COLLS_MENU= '📜Revision collocations'
MESS_REVISION_COLLS_MENU = "Choose colls!"
BTEXT_REVISION_COLLS_MENU_BACK = "📜Collocations"
# show links
CALL_SHOW_TASKS = "show_links_"
MESS_SHOW_TASKS = 'Выберите коллокацию'
NUM_SHOW_TASKS_COLS = 1
NUM_SHOW_TASKS_ROWS = 5
CHECK_REVISION_TASKS= '🟣'


CALL_ADDING_MENU = "@c_adm_menu_add"
MESS_ADDING_MENU = "Choose what do you want to add"
BTEXT_ADDING_MENU = "📌Add words, collocation and other📌"
BTEXT_ADDING_MENU_BACK = "🛠️Adding"

CALL_EDITING_MENU = "c_adm_menu_edit"
MESS_EDITING_MENU = "Choose what do you want to edit"
BTEXT_EDITING_MENU = "Editing"
BTEXT_EDITING_MENU_BACK = "🛠️Editing"

CALL_UPDATE_USER_INTERVALS = "@c_update_user_intervals"
BTEXT_UPDATE_USER_INTERVALS = "*Temp*Update user intervals"

CALL_DELETE_TEST_MEDIA = "@c_delete_test_media"
BTEXT_DELETE_TEST_MEDIA = "*Temp*Delete test media"

CALL_SETTING_MENU = "@c_adm_menu_set"
MESS_SETTING_MENU = "Choose what do you want to set or assign"
BTEXT_SETTING_MENU = "📌Set task to user📌"
BTEXT_SETTING_MENU_BACK = "🛠️Set menu-"

CALL_ADD_SOURCE= 'c_add_source_'
BTEXT_ADD_SOURCE = "📌Add source📌"
CALL_EDIT_SOURCE= 'c_edit_source_'
BTEXT_EDIT_SOURCE = "📌Edit source📌"

CALL_ADD_WORD= 'c_add_word_'
BTEXT_ADD_WORD = "📌Add word📌"
CALL_EDIT_WORD= 'c_edit_word_'
BTEXT_EDIT_WORD = "📌Edit word📌"

CALL_ADD_COLL= 'c_add_coll_'
BTEXT_ADD_COLL = "📌Add collocation📌"
CALL_EDIT_COLL= 'c_edit_coll_'
BTEXT_EDIT_COLL = "📌Edit collocation📌"

CALL_ADD_TEST = "c_add_test_"
BTEXT_ADD_TEST = "📌Add test📌"

CALL_ADD_LINK = "c_add_link_"
BTEXT_ADD_LINK = "📌Add link📌"
CALL_EDIT_LINK = "c_edit_link_"
BTEXT_EDIT_LINK = "📌Edit link📌"

CALL_ADD_GROUP = "c_add_group_"
BTEXT_ADD_GROUP = "📌Add group📌"
CALL_EDIT_GROUP = "c_edit_group_"
BTEXT_EDIT_GROUP = "📌Edit group📌"

CALL_ADD_HOMEWORK = "c_add_homework_"
BTEXT_ADD_HOMEWORK = "📌Add homework📌"
CALL_EDIT_HOMEWORK = "c_edit_homework_"
BTEXT_EDIT_HOMEWORK = "📌Edit homework📌"


CALL_SET_SCHEME= 'c_set_scheme_'
BTEXT_SET_SCHEME = "📌Set task by scheme📌"

CALL_SET_COLL = "c_set_coll"
BTEXT_SET_COLL = "Set task with some collocation"




# common
MESS_CHANGING = 'Внесите изменения!'
MESS_MORE_CHOOSING = 'Можете выбрать еще или нажмите подтверждение'
MESS_NULL_CHOOSING = 'Нельзя продолжить пока ничего не выбрано'
MESS_ADDED_TO_DB = 'Информация добавлена в базу данных!'
MESS_ERROR_ADDED_TO_DB = 'Ошибка при записи в базу данных, обратитесь к администратору'
CALL_CONFIRM= "@confirm_"
BTEXT_CONFIRM= "✅CONFIRM✅"
NUM_MAX_CALL_ALARM_LENGTH = 192
MESS_TOO_LONG = "Длина введенного текста превышает максимально допустимую на {} символов. Попробуйте еще раз."


MESS_ADD_ENDING = 'Поверьте все и подтвердите'
CALL_ADD_ENDING = "add_ending_"




# capturing word
CALL_CAPTURE_WORDS = "capture_words_"
CALL_CHANGING_WORDS = "changing_words_"
MESS_CAPTURE_WORDS = 'Выберите слово или введите с клавиатуры и отправьте боту часть этого слова (его номер)'
BTEXT_CHANGE_WORDS = "Изменить слова"
MESS_NO_WORDS = 'Список слов пуст'
NUM_CAPTURE_WORDS_COLS = 2
NUM_CAPTURE_WORDS_ROWS = 10
CHECK_CAPTURE_WORDS= '🟣'

# capturing collocations
CALL_CAPTURE_COLLS = "capture_colls_"
CALL_CHANGING_COLLS = "changing_colls_"
MESS_CAPTURE_COLLS = 'Выберите коллокацию или введите с клавиатуры и отправьте боту ее часть'
BTEXT_CHANGE_COLLS = "Изменить коллокации"
MESS_NO_COLLS = 'Список коллокаций пуст'
NUM_CAPTURE_COLLS_COLS = 2
NUM_CAPTURE_COLLS_ROWS = 10
CHECK_CAPTURE_COLLS= '🟣'

# show colls
MESS_REVISION_COLLS = 'Выберите коллокацию или введите ее часть'
NUM_REVISION_COLLS_COLS = 2
NUM_REVISION_COLLS_ROWS = 5
CHECK_REVISION_COLLS= '🟣'

# show colls
MESS_QUICK_TASKS = 'Выберите коллокацию'
NUM_QUICK_TASK_COLS = 1
NUM_QUICK_TASK_ROWS = 1
CHECK_QUICK_TASK = '🟣'


# capturing part
CALL_CAPTURE_PARTS = "capture_parts_"
CALL_CHANGING_PARTS = "changing_parts_"
MESS_CAPTURE_PARTS = 'Выберите часть речи или введите с клавиатуры и отправьте боту часть названия'
BTEXT_CHANGE_PARTS = "Изменить часть речи"
NUM_CAPTURE_PARTS_COLS = 3
NUM_CAPTURE_PARTS_ROWS = 10
CHECK_CAPTURE_PARTS= '🟣'
PARTS_LIST = ['noun', 'verb', 'adjective', 'adverb', 'pronoun', 'numerals', 'idiom', 'phrasal verb', 'new2']

# capturing source
CALL_CAPTURE_SOURCES = "capture_sources_"
CALL_CHANGING_SOURCES = "changing_sources_"
MESS_CAPTURE_SOURCES = 'Выберите источник или введите с клавиатуры и отправьте боту часть названия'
MESS_NO_SOURCES = 'Список источников пуст'
BTEXT_CHANGE_SOURCES = "Изменить источник"
NUM_CAPTURE_SOURCES_COLS = 1
NUM_CAPTURE_SOURCES_ROWS = 10
CHECK_CAPTURE_SOURCES= '🟣'

# capturing level
CALL_CAPTURE_LEVELS = "capture_levels_"
CALL_CHANGING_LEVELS = "changing_levels_"
MESS_CAPTURE_LEVELS = 'Выберите уровень или введите с клавиатуры и отправьте боту часть названия'
BTEXT_CHANGE_LEVELS = "Изменить уровень"
NUM_CAPTURE_LEVELS_COLS = 3
NUM_CAPTURE_LEVELS_ROWS = 10
CHECK_CAPTURE_LEVELS= '🟣'
LEVELS_LIST = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

# capturing group
CALL_CAPTURE_GROUPS = "capture_groups_"
CALL_CHANGING_GROUPS = "changing_groups_"
MESS_CAPTURE_GROUPS = 'Выберите группу или введите с клавиатуры и отправьте боту часть названия группы (ее номер)'
BTEXT_CHANGE_GROUPS = "Изменить группу"
MESS_NO_GROUPS = 'Список групп пуст'
NUM_CAPTURE_GROUPS_COLS = 1
NUM_CAPTURE_GROUPS_ROWS = 10
CHECK_CAPTURE_GROUPS= '🟣'

# capturing user
CALL_CAPTURE_USERS = "capture_users_"
CALL_CHANGING_USERS = "changing_users_"
MESS_CAPTURE_USERS = 'Выберите пользователя или введите с клавиатуры и отправьте боту часть его имени (или номер)'
MESS_NO_USERS = 'Список пользователей пуст'
BTEXT_CHANGE_USERS = "Изменить юзеров"
NUM_CAPTURE_USERS_COLS = 2
NUM_CAPTURE_USERS_ROWS = 10
CHECK_CAPTURE_USERS= '🟣'

# capturing date
CALL_CAPTURE_DATES = "capture_dates_"
CALL_CHANGING_DATES = "changing_dates_"
MESS_CAPTURE_DATES = 'Выберите дату'
BTEXT_CHANGE_DATES = "Изменить дату"
NUM_CAPTURE_DATES_COLS = 4
NUM_CAPTURE_DATES_ROWS = 5
CHECK_CAPTURE_DATES= '🟣'

# capturing date
CALL_CAPTURE_PRIRITY = "capture_priority_"
CALL_CHANGING_PRIRITY = "changing_priority_"
MESS_CAPTURE_PRIRITY = 'Выберите приорирет'
BTEXT_CHANGE_PRIRITY = "Изменить приоритет"
NUM_CAPTURE_PRIRITY_COLS = 5
NUM_CAPTURE_PRIRITY_ROWS = 2
CHECK_CAPTURE_PRIRITY= '🟣'


# capturing day
CALL_CAPTURE_DAYS = "capture_daуs_"
CALL_CHANGING_DAYS = "changing_days_"
MESS_CAPTURE_DAYS = 'Выберите день изучения или введите с клавиатуры и отправьте боту часть слова'
BTEXT_CHANGE_DAYS = "Изменить дeнь"
NUM_CAPTURE_DAYS_COLS = 4
NUM_CAPTURE_DAYS_ROWS = 8
CHECK_CAPTURE_DAYS= '🟣'

# capturing homeworks
CALL_CAPTURE_HOMEWORKS = "capture_homeworks_"
CALL_CHANGING_HOMEWORKS = "changing_homeworks_"
MESS_CAPTURE_HOMEWORKS = 'Выберите домашнее задание или введите с клавиатуры и отправьте боту часть названия группы (ее номер)'
BTEXT_CHANGE_HOMEWORKS = "Изменить домашнее задание"
MESS_NO_HOMEWORKS = 'Список домашних заданий пуст'
NUM_CAPTURE_HOMEWORKS_COLS = 1
NUM_CAPTURE_HOMEWORKS_ROWS = 5
CHECK_CAPTURE_HOMEWORKS= '🟣'


CALL_CAPTURE_LINKS = "capture_links_"
CALL_CHANGING_LINKS = "changing_links_"
MESS_CAPTURE_LINKS = 'Выберите ссылку'
BTEXT_CHANGE_LINKS = "Изменить ссылку"
MESS_NO_LINKS = 'Список ссылок заданий пуст'
NUM_CAPTURE_LINKS_COLS = 1
NUM_CAPTURE_LINKS_ROWS = 5
CHECK_CAPTURE_LINKS= '🟣'


# input source
CALL_INPUT_SOURCE_NAME = "input_source_"
CALL_CHANGING_SOURCE_NAME = "changing_source_name_"
MESS_INPUT_SOURCE_NAME = "Введите имя источника"
MESS_INPUT_SOURCE_NAME_ALREADY_EXIST = "Такой источник уже существует, попробуйте ввести имя источника еще раз"
BTEXT_CHANGE_SOURCE_NAME = "Изменить источник"
# input word
CALL_INPUT_WORD = "input_word_"
CALL_CHANGING_WORD = "changing_word_"
MESS_INPUT_WORD = "Введите слово для словаря"
MESS_INPUT_WORD_ALREADY_EXIST = "Такое слово уже существует, попробуйте ввести слово для словаря еще раз"
BTEXT_CHANGE_WORD = "Изменить слово"
# input group
CALL_INPUT_GROUP = "input_group_"
CALL_CHANGING_GROUP = "changing_group_"
MESS_INPUT_GROUP = "Введите название группы"
MESS_INPUT_GROUP_ALREADY_EXIST = "Такая группа уже существует, попробуйте ввести другое наименование"
BTEXT_CHANGE_GROUP = "Изменить название группы"
# input homework
CALL_INPUT_HOMEWORK = "input_homework_"
CALL_CHANGING_HOMEWORK = "changing_homework_"
MESS_INPUT_HOMEWORK = "Введите домашнее задание"
BTEXT_CHANGE_HOMEWORK = "Изменить домашнее задание"
# input link name
CALL_INPUT_LINK_NAME = "input_link_name"
CALL_CHANGING_LINK_NAME = "changing_link_name_"
MESS_INPUT_LINK_NAME = "Введите наименование ссылки"
BTEXT_CHANGE_LINK_NAME = "Изменить наименование ссылки"
# input link url
CALL_INPUT_LINK_URL = "input_link_url"
CALL_CHANGING_LINK_URL = "changing_link_url_"
MESS_INPUT_LINK_URL = "Введите url ссылки"
BTEXT_CHANGE_LINK_URL = "Изменить url ссылки"
# input collocation
CALL_INPUT_COLL = "input_coll_"
CALL_CHANGING_COLL = "changing_coll_"
MESS_INPUT_COLL = "Введите коллокацию для изучаемого слова"
BTEXT_CHANGE_COLL = "Изменить коллокацию"
# input media
CALL_INPUT_MEDIA = "input_media_"
CALL_CHANGING_MEDIA = "changing_media_"
MESS_INPUT_MEDIA = "Добавьте медиа: введите текст, отправьте картинку или видео"
BTEXT_CHANGE_MEDIA = "Изменить медиа"
# input caption
CALL_INPUT_CAPTION = "input_caption_"
CALL_CHANGING_CAPTION = "changing_caption_"
MESS_INPUT_CAPTION = "Введите caption"
BTEXT_CHANGE_CAPTION = "Изменить caption"
# input definition
CALL_INPUT_DEFINITION = "input_definition_"
CALL_CHANGING_DEFINITION = "changing_definition_"
MESS_INPUT_DEFINITION = "Введите определение на английском языке"
BTEXT_CHANGE_DEFINITION = "Изменить определение"
# input translation
CALL_INPUT_TRANSLATION = "input_translation_"
CALL_CHANGING_TRANSLATION = "changing_translation_"
MESS_INPUT_TRANSLATION = "Введите русский перевод"
BTEXT_CHANGE_TRANSLATION = "Изменить перевод"

