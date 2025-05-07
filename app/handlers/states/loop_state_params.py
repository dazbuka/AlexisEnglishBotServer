from typing import Optional
from aiogram.types import InlineKeyboardButton
from aiogram.fsm.state import State

from app.common_settings import *
from app.database.requests import get_users_by_filters, get_words_by_filters, get_sources_by_filters, \
    get_groups_by_filters, get_medias_by_filters, get_homeworks_by_filters, get_links_by_filters
from config import logger
from app.database.models import UserStatus
from datetime import date, timedelta


class InputStateParams:

    def __init__(self,
                 self_state: State,
                 menu_pack : list[list[InlineKeyboardButton]],
                 call_base: str,
                 main_mess: Optional[str] = None,
                 # необязательные параметры клавиатуры
                 buttons_pack: Optional[list[InlineKeyboardButton]] = None,
                 buttons_cols: Optional[int] = None,
                 buttons_rows: Optional[int] = None,
                 buttons_check: Optional[str] = None,
                 # необязательные параметры для перехода в следующий State
                 next_state: Optional[State] = None,
                 # необязательные логические флаги
                 is_can_be_empty: bool = False,
                 is_only_one : bool = False,
                 is_last_state_with_changing_mode: bool = False,
                 is_input: bool = False,
                 is_media_revision_mode: bool = False
                 ) -> None:

        # Вводимые значения
        self.input_text : Optional[str] = None
        self.set_of_items: Optional[set] = set()
        self.media_id : Optional[str] = None
        self.media_type : Optional[str] = None

        # Параметры, передаваемые в функцию
        self.self_state = self_state #
        self.menu_pack = menu_pack  #
        self.call_base = call_base #
        self.main_mess = main_mess  #

        # Параменты набора кнопок клавиатуры
        self.buttons_pack = buttons_pack
        self.buttons_cols = buttons_cols
        self.buttons_rows = buttons_rows
        self.buttons_check = buttons_check

        # необязательный параметр для перехода в следующий State
        self.next_state = next_state

        # логические флаги
        self.is_can_be_empty = is_can_be_empty
        self.is_only_one = is_only_one  # выбор только одного элемента
        self.is_last_state_with_changing_mode = is_last_state_with_changing_mode  #
        self.is_input = is_input
        self.is_media_revision_mode = is_media_revision_mode


    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(state={self.self_state}, "
            f"menu_pack=<matrix of size {len(self.menu_pack)}x{max(len(row) for row in self.menu_pack) if self.menu_pack else 0}>, "
            f"call_base='{self.call_base}', "
            f"main_mess='{self.main_mess}', "
            f"buttons_pack={'present' if self.buttons_pack else 'absent'}, "
            f"buttons_cols={self.buttons_cols}, "
            f"buttons_rows={self.buttons_rows}, "
            f"buttons_check='{self.buttons_check or ''}', "
            f"next_state={'present' if self.next_state else 'absent'}, "
            f"input_text='{self.input_text or ''}', "
            f"set_of_items='{self.set_of_items or ''}', "
            f"media_id='{self.media_id or ''}', "
            f"media_type='{self.media_type or ''}', "
            f"is_can_be_empty={self.is_can_be_empty}, "
            f"is_only_one={self.is_only_one}, "
            f"is_last_state_with_changing_mode={self.is_last_state_with_changing_mode}, "
            f"is_input={self.is_input})"
        )

    async def update_state_for_colls_capture(self, colls_filter: str = 'all') -> None:
        """
        Обновляет пакет кнопок и базовый callback для выбора коллокаций.
        Args:
            colls_filter (str): Определяет фильтр для выбора коллокаций.
        """
        self.main_mess = MESS_CAPTURE_COLLS
        self.buttons_cols = NUM_CAPTURE_COLLS_COLS
        self.buttons_rows = NUM_CAPTURE_COLLS_ROWS
        self.buttons_check = CHECK_CAPTURE_COLLS

        try:
            if colls_filter == 'all':
                colls_list = await get_medias_by_filters()
            elif colls_filter == 'media':
                colls_list = await get_medias_by_filters(media_only=True)
            else:
                logger.warning('Некорректный фильтр коллокаций.')
                return

            if not colls_list:
                self.main_mess = MESS_NO_COLLS
                logger.warning('Список коллокаций пуст. Кнопки не обновлены.')
                return

            # Формируем клавиатуру
            colls_kb = [
                InlineKeyboardButton(text=f'{coll.collocation}', callback_data=f'{self.call_base}{coll.id}')
                for coll in colls_list]

            colls_kb_reversed = colls_kb[::-1]

            # Устанавливаем значение
            self.buttons_pack = colls_kb_reversed
        except Exception as e:
            logger.error(
                f'Произошла ошибка при получении коллокаций при обновлении класса CaptureCollsStateParams: {e}')

    async def update_state_for_colls_revision(self, colls_set = None, word_id = None, colls_filter: str = 'all') -> None:
        """
        Обновляет пакет кнопок и базовый callback для выбора коллокаций.
        Args:
            colls_filter (str): Определяет фильтр для выбора коллокаций.
        """

        self.main_mess = MESS_REVISION_COLLS
        self.buttons_cols = NUM_REVISION_COLLS_COLS
        self.buttons_rows = NUM_REVISION_COLLS_ROWS
        self.buttons_check = CHECK_REVISION_COLLS

        try:
            if colls_set:
                colls_list = await get_medias_by_filters(media_id_set=colls_set)
            elif word_id:
                colls_list = await get_medias_by_filters(word_id=word_id)
            elif colls_filter == 'all':
                colls_list = await get_medias_by_filters()
            elif colls_filter == 'media':
                colls_list = await get_medias_by_filters(media_only=True)
            else:
                logger.warning('Некорректный фильтр коллокаций.')
                return

            if not colls_list:
                self.main_mess = MESS_NO_COLLS
                self.buttons_pack = []
                logger.warning('Список коллокаций пуст. Кнопки не обновлены.')
                return

            # Формируем клавиатуру
            colls_kb = [
                InlineKeyboardButton(text=f'{coll.collocation}', callback_data=f'{self.call_base}{coll.id}')
                for coll in colls_list]

            colls_kb_reversed = colls_kb[::-1]

            # Устанавливаем значение
            self.buttons_pack = colls_kb_reversed
        except Exception as e:
            logger.error(
                f'Произошла ошибка при получении коллокаций при обновлении класса CaptureCollsStateParams: {e}')

    async def update_state_for_quick_tasks(self, colls_set = None, colls_filter: str = 'all') -> None:
        """
        Обновляет пакет кнопок и базовый callback для выбора коллокаций.
        Args:
            colls_filter (str): Определяет фильтр для выбора коллокаций.
            colls_set (set): Определяет список пользователей (он будет один) которому ищем задание
        """

        self.main_mess = MESS_QUICK_TASKS
        self.buttons_cols = NUM_QUICK_TASK_COLS
        self.buttons_rows = NUM_QUICK_TASK_ROWS
        self.buttons_check = CHECK_QUICK_TASK

        try:
            if colls_set:
                colls_list = await get_medias_by_filters(media_id_set=colls_set)
            elif colls_filter == 'all':
                colls_list = await get_medias_by_filters()
            elif colls_filter == 'media':
                colls_list = await get_medias_by_filters(media_only=True)
            else:
                logger.warning('Некорректный фильтр коллокаций.')
                return

            if not colls_list:
                self.main_mess = MESS_NO_COLLS
                self.buttons_pack = []
                logger.warning('Список коллокаций пуст. Кнопки не обновлены.')
                return

            # Формируем клавиатуру
            colls_kb = [
                InlineKeyboardButton(text=f'{coll.collocation}', callback_data=f'{self.call_base}{coll.id}')
                for coll in colls_list]

            colls_kb_reversed = colls_kb[::-1]

            # Устанавливаем значение
            self.buttons_pack = colls_kb_reversed
        except Exception as e:
            logger.error(
                f'Произошла ошибка при получении коллокаций при обновлении класса CaptureCollsStateParams: {e}')

    async def update_state_for_users_capture(self, users_filter: str = 'all') -> None:
        self.main_mess = MESS_CAPTURE_USERS
        self.buttons_cols = NUM_CAPTURE_USERS_COLS
        self.buttons_rows = NUM_CAPTURE_USERS_ROWS
        self.buttons_check = CHECK_CAPTURE_USERS

        try:
            if users_filter == 'active':
                users_list = await get_users_by_filters(status=UserStatus.ACTIVE)
            elif users_filter == 'all':
                users_list = await get_users_by_filters()
            elif users_filter == 'test':
                users_list = await get_users_by_filters(user_tg_id=1)
            else:
                logger.warning('Некорректный фильтр пользователей.')
                return

            if not users_list:
                self.main_mess = MESS_NO_USERS
                logger.warning('Список пользователей пуст. Кнопки не обновлены.')
                return

            # Формируем клавиатуру
            users_kb = [InlineKeyboardButton(text=f'{user.ident_name}', callback_data=f'{self.call_base}{user.id}')
                        for user in users_list]

            # Устанавливаем значение
            self.buttons_pack = users_kb
        except Exception as e:
            logger.error(
                f'Произошла ошибка при получении пользователей при обновлении класса CaptureUsersStateParams: {e}')

    async def update_state_for_words_capture(self, words_filter: str = 'all') -> None:
        self.main_mess = MESS_CAPTURE_WORDS
        self.buttons_cols = NUM_CAPTURE_WORDS_COLS
        self.buttons_rows = NUM_CAPTURE_WORDS_ROWS
        self.buttons_check = CHECK_CAPTURE_WORDS
        try:
            if words_filter == 'all':
                words_list = await get_words_by_filters()
            else:
                logger.warning('Некорректный фильтр слов.')
                return

            if not words_list:
                self.main_mess = MESS_NO_WORDS
                logger.warning('Список слов пуст. Кнопки не обновлены.')
                return

            # Формируем клавиатуру
            words_kb = [
                InlineKeyboardButton(text=f'{word.word}', callback_data=f'{self.call_base}{word.id}')
                for word in words_list]

            words_kb_reversed = words_kb[::-1]
            # Устанавливаем значение
            self.buttons_pack = words_kb_reversed
        except Exception as e:
            logger.error(
                f'Произошла ошибка при получении слов при обновлении класса CaptureWordsStateParams: {e}')

    async def update_state_for_words_revision(self, words_set = None, source_id = None, words_filter: str = 'all') -> None:
        self.main_mess = MESS_REVISION_WORDS_MENU
        self.buttons_cols = NUM_REVISION_WORDS_COLS
        self.buttons_rows = NUM_REVISION_WORDS_ROWS
        self.buttons_check = CHECK_REVISION_WORDS
        try:
            if words_set:
                words_list = await get_words_by_filters(word_id_set=words_set)
            elif source_id:
                words_list = await get_words_by_filters(source_id=source_id)
            elif words_filter == 'all':
                words_list = await get_words_by_filters()
            else:
                logger.warning('Некорректный фильтр слов.')
                return

            if not words_list:
                self.main_mess = MESS_NO_WORDS
                logger.warning('Список слов пуст. Кнопки не обновлены.')
                return

            # Формируем клавиатуру
            words_kb = [
                InlineKeyboardButton(text=f'{word.word}', callback_data=f'{self.call_base}{word.id}')
                for word in words_list]

            words_kb_reversed = words_kb[::-1]
            # Устанавливаем значение
            self.buttons_pack = words_kb_reversed
        except Exception as e:
            logger.error(
                f'Произошла ошибка при получении слов при обновлении класса CaptureWordsStateParams: {e}')

    async def update_state_for_groups_capture(self, groups_filter: str = 'all') -> None:
        self.main_mess = MESS_CAPTURE_GROUPS
        self.buttons_cols = NUM_CAPTURE_GROUPS_COLS
        self.buttons_rows = NUM_CAPTURE_GROUPS_ROWS
        self.buttons_check = CHECK_CAPTURE_GROUPS
        try:
            if groups_filter == 'all':
                groups_list = await get_groups_by_filters()
            else:
                logger.warning('Некорректный фильтр групп.')
                return

            if not groups_list:
                self.main_mess = MESS_NO_WORDS
                logger.warning('Список групп пуст. Кнопки не обновлены.')
                return

            # Формируем клавиатуру
            groups_kb = [
                InlineKeyboardButton(text=f'{group.name}', callback_data=f'{self.call_base}{group.id}')
                for group in groups_list]

            # Устанавливаем значение
            self.buttons_pack = groups_kb
        except Exception as e:
            logger.error(
                f'Произошла ошибка при получении групп при обновлении класса CaptureGroupsStateParams: {e}')

    async def update_state_for_homeworks_capture(self, homeworks_filter: str = 'all') -> None:
        self.main_mess = MESS_CAPTURE_HOMEWORKS
        self.buttons_cols = NUM_CAPTURE_HOMEWORKS_COLS
        self.buttons_rows = NUM_CAPTURE_HOMEWORKS_ROWS
        self.buttons_check = CHECK_CAPTURE_HOMEWORKS
        try:
            if homeworks_filter == 'all':
                homeworks_list = await get_homeworks_by_filters()
            elif homeworks_filter == 'actual':
                homeworks_list = await get_homeworks_by_filters()
            else:
                logger.warning('Некорректный фильтр домашних заданий.')
                return

            if not homeworks_list:
                self.main_mess = MESS_NO_HOMEWORKS
                logger.warning('Список домашних заданий пуст. Кнопки не обновлены.')
                return

            # Формируем клавиатуру
            homeworks_kb = [
                InlineKeyboardButton(text=f'{homework.hometask}', callback_data=f'{self.call_base}{homework.id}')
                for homework in homeworks_list]

            # Устанавливаем значение
            self.buttons_pack = homeworks_kb
        except Exception as e:
            logger.error(
                f'Произошла ошибка при получении групп при обновлении класса CaptureHomeworksStateParams: {e}')

    async def update_state_for_links_capture(self, user_id = None, links_filter: str = 'all') -> None:
        self.main_mess = MESS_CAPTURE_LINKS
        self.buttons_cols = NUM_CAPTURE_LINKS_COLS
        self.buttons_rows = NUM_CAPTURE_LINKS_ROWS
        self.buttons_check = CHECK_CAPTURE_LINKS

        try:
            if user_id:
                links_list = await get_links_by_filters(user_id=user_id)
            elif links_filter == 'all':
                links_list = await get_links_by_filters()
            else:
                logger.warning('Некорректный фильтр домашних заданий.')
                return

            if not links_list:
                self.main_mess = MESS_NO_LINKS
                logger.warning('Список домашних заданий пуст. Кнопки не обновлены.')
                return

            # Формируем клавиатуру
            links_kb = [
                InlineKeyboardButton(text=f'{link.name}', callback_data=f'{self.call_base}{link.id}')
                for link in links_list]

            # Устанавливаем значение
            self.buttons_pack = links_kb
        except Exception as e:
            logger.error(
                f'Произошла ошибка при получении ссылок при обновлении класса CaptureLinksStateParams: {e}')

    async def update_state_for_sources_capture(self, sources_filter: str = 'all') -> None:
        self.main_mess = MESS_CAPTURE_SOURCES
        self.buttons_cols = NUM_CAPTURE_SOURCES_COLS
        self.buttons_rows = NUM_CAPTURE_SOURCES_ROWS
        self.buttons_check = CHECK_CAPTURE_SOURCES
        try:
            if sources_filter == 'all':
                sources_list = await get_sources_by_filters()
            else:
                logger.warning('Некорректный фильтр источника.')
                return

            if not sources_list:
                self.main_mess = MESS_NO_SOURCES
                logger.warning('Список источников пуст. Кнопки не обновлены.')
                return

            # Формируем клавиатуру
            sources_kb = [
                InlineKeyboardButton(text=f'{source.source_name}', callback_data=f'{self.call_base}{source.id}')
                for source in sources_list]

            # Устанавливаем значение
            self.buttons_pack = sources_kb
        except Exception as e:
            logger.error(
                f'Произошла ошибка при получении источников при обновлении класса CaptureSourcesStateParams: {e}')

    async def update_state_for_sources_revision(self, sources_set = None, sources_filter: str = 'all') -> None:
        self.main_mess = MESS_REVISION_SOURCES
        self.buttons_cols = NUM_REVISION_SOURCES_COLS
        self.buttons_rows = NUM_REVISION_SOURCES_ROWS
        self.buttons_check = CHECK_REVISION_SOURCES
        try:
            if sources_set:
                sources_list = await get_sources_by_filters(source_id_set=sources_set)
            elif sources_filter == 'one':
                sources_list = await get_sources_by_filters(source_id=1)
            else:

                logger.warning('Некорректный фильтр источника.')
                return

            if not sources_list:
                self.main_mess = MESS_NO_SOURCES
                logger.warning('Список источников пуст. Кнопки не обновлены.')
                return

            # Формируем клавиатуру
            sources_kb = [
                InlineKeyboardButton(text=f'{source.source_name}', callback_data=f'{self.call_base}{source.id}')
                for source in sources_list]

            # Устанавливаем значение
            self.buttons_pack = sources_kb
        except Exception as e:
            logger.error(
                f'Произошла ошибка при получении источников при обновлении класса CaptureSourcesStateParams: {e}')

    async def update_state_for_dates_capture(self) -> None:
        self.main_mess = MESS_CAPTURE_DATES
        self.buttons_cols = NUM_CAPTURE_DATES_COLS
        self.buttons_rows = NUM_CAPTURE_DATES_ROWS
        self.buttons_check = CHECK_CAPTURE_DATES
        self.buttons_pack = [InlineKeyboardButton(
            text=f'{(date.today() + timedelta(days=i)).strftime("%d.%m.%Y")}',
            callback_data=f'{self.call_base}{(date.today() + timedelta(days=i)).strftime("%d.%m.%Y")}'
            ) for i in range(1, 150)]

    async def update_state_for_priority_capture(self) -> None:
        self.main_mess = MESS_CAPTURE_PRIRITY
        self.buttons_cols = NUM_CAPTURE_PRIRITY_COLS
        self.buttons_rows = NUM_CAPTURE_PRIRITY_ROWS
        self.buttons_check = CHECK_CAPTURE_PRIRITY
        self.buttons_pack = [InlineKeyboardButton(text=f'{priority}', callback_data=f'{self.call_base}{priority}')
                                  for priority in range(1,11)]

    async def update_state_for_days_capture(self) -> None:
        self.main_mess = MESS_CAPTURE_DAYS
        self.buttons_cols = NUM_CAPTURE_DAYS_COLS
        self.buttons_rows = NUM_CAPTURE_DAYS_ROWS
        self.buttons_check = CHECK_CAPTURE_DAYS
        self.buttons_pack = [InlineKeyboardButton(text=f'{day}', callback_data=f'{self.call_base}{day}')
                                  for day in range(150)]

    def update_state_for_sending_time_capture(self) -> None:
        self.main_mess = MESS_CONFIG_SENDING_TIME
        self.buttons_cols = NUM_CONFIG_SENDING_TIME_COLS
        self.buttons_rows = NUM_CONFIG_SENDING_TIME_ROWS
        self.buttons_check = CHECK_CONFIG_SENDING_TIME
        self.buttons_pack = [InlineKeyboardButton(text=f'{str(hour).zfill(2)}:00',
                                                  callback_data=f'{self.call_base}{str(hour).zfill(2)}:00')
                                                  for hour in range(7,23)]

    async def update_state_for_parts_capture(self) -> None:
        self.main_mess = MESS_CAPTURE_PARTS
        self.buttons_cols = NUM_CAPTURE_PARTS_COLS
        self.buttons_rows = NUM_CAPTURE_PARTS_ROWS
        self.buttons_check = CHECK_CAPTURE_PARTS
        self.buttons_pack = [InlineKeyboardButton(text=f'{part}', callback_data=f'{self.call_base}{part}')
                     for part in PARTS_LIST]

    async def update_state_for_level_capture(self) -> None:
        self.main_mess = MESS_CAPTURE_LEVELS
        self.buttons_cols = NUM_CAPTURE_LEVELS_COLS
        self.buttons_rows = NUM_CAPTURE_LEVELS_ROWS
        self.buttons_check = CHECK_CAPTURE_LEVELS
        self.buttons_pack = [InlineKeyboardButton(text=f'{level}', callback_data=f'{self.call_base}{level}')
                     for level in LEVELS_LIST]

    async def update_state_for_confirmation_state(self) -> None:
        self.main_mess = MESS_ADD_ENDING


