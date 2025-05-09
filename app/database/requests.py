from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import func
from sqlalchemy import BigInteger
from config import bot, DEVELOPER_ID
from app.database.models import async_session
from app.database.models import User, Task, Media, Word, Source, Homework, Group, Link
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from config import logger
from datetime import timedelta, datetime, time, date
from aiogram.types import Message
from app.database.models import UserStatus
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

# запросы по таблице users

# первичное добавление пользователя, функция срабатывает при нажатии кнопки старт
async def set_user(message : Message):
    try:
        async with (async_session() as session):
            user = await session.scalar(select(User).where(User.telegram_id == message.chat.id))
            if not user:
                if not message.chat.username:
                    username = message.chat.first_name
                else:
                    username = message.chat.username
                first_name = message.chat.first_name
                last_name = message.chat.last_name

                i_n_1 = f'{username} ({first_name}'
                i_n_2 = f' {last_name})' if last_name is not None else ')'
                ident_name = i_n_1 + i_n_2
                session.add(User(telegram_id=message.chat.id,
                                 username=username,
                                 first_name=first_name,
                                 last_name=last_name,
                                 ident_name = ident_name,
                                 last_message_id = message.message_id))
                await session.commit()
                logger.info(f"Зарегистрировал пользователя с ID {message.chat.id} - {message.chat.username} "
                            f"- {message.chat.first_name} - {message.chat.last_name}!")
                await bot.send_message(DEVELOPER_ID, f"Зарегистрировал пользователя с ID {message.from_user.id} - "
                                               f"{message.from_user.username} - {message.from_user.first_name} "
                                               f"- {message.from_user.last_name}!")
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении пользователя "
                     f"{message.from_user.username} ({message.from_user.id}): {e}")
        await session.rollback()


#изменение времени отправления сообщений
async def update_user_intervals(user_tg_id: int, intervals : str):
    async with (async_session() as session):
        user = await session.scalar(select(User).where(User.telegram_id == user_tg_id))
        if user:
            user.intervals = intervals
            await session.commit()
        else:
            logger.info(f'Ошибка при изменении интервалов оповещения для пользователя {user_tg_id} ({intervals})')

#изменение времени отправления сообщений
async def update_user_intervals_temp_alembic(user_id: int, intervals : str):
    async with (async_session() as session):
        user = await session.scalar(select(User).where(User.id == user_id))
        if user:
            user.intervals = intervals
            await session.commit()
        else:
            logger.info(f'Ошибка при изменении интервалов оповещения для пользователя {user_id} ({intervals})')

#изменение статуса пользователя
async def update_user_status(user_tg_id: int, status : str):
    async with (async_session() as session):
        user = await session.scalar(select(User).where(User.telegram_id == user_tg_id))
        if user:
            user.status = status
            await session.commit()
        else:
            logger.info(f'Ошибка при изменении статуса пользлователя {user_tg_id} ({status})')


#изменение номера последнего сообщения
async def update_user_last_message_id(user_tg_id: int | BigInteger, message_id: int):
    async with (async_session() as session):
        user = await session.scalar(select(User).where(User.telegram_id == user_tg_id))
        if user:
            user.last_message_id = message_id
            await session.commit()
        else:
            logger.info(f'Ошибка при изменении номера последнего сообщения для пользователя {user_tg_id} ({message_id})')


# функция получения номер последнего сообщения пользователя из базы данных
async def get_user_last_message_id(user_tg_id: int) -> int:
    async with (async_session() as session):
        user = await session.scalar(select(User).where(User.telegram_id == user_tg_id))
        last_msg = 0
        if user:
            if user.last_message_id:
                last_msg = int(user.last_message_id)
        else:
            logger.info(f"Ошибка! Не могу определить номер последнего сообщения для {user_tg_id}")
        return last_msg

# поиск пользователя по фильтрам
async def get_users_by_filters(user_id: int = None,
                               user_tg_id: int | BigInteger  = None,
                               limit: int = 30,
                               status: str = None):
    async with async_session() as session:
        try:
            selection = select(User).options(selectinload(User.tasks))

            if user_id:
                selection = selection.filter_by(id = user_id)

            if user_tg_id:
                selection = selection.filter_by(telegram_id = user_tg_id)

            if status:
                selection = selection.filter_by(status = status)

            if limit:
                selection = selection.order_by(User.id.desc()).limit(limit)

            rezult = await session.execute(selection)
            users = rezult.scalars().all()

            if not users:
                logger.info(f"не нашел user в базе данных")
            else:
                # если пользователь найден один - возвращаем его, если найдено много - возвращаем всех
                if len(users)==1:
                    return users[0]
                else:
                    return users
                # return users
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске users: {e}")



 # добавление source в базу данных, ничего не возвращает
async def add_source_to_db(source_name, author_id) -> bool:
    async with async_session() as session:
        try:
            source_in_db = await session.scalar(select(Source).where(Source.source_name == source_name))
            if not source_in_db:
                session.add(Source(source_name=source_name,
                                   author_id=author_id))
                await session.commit()
                logger.info(f"В базу данных добавлен source  {source_name}!")
            else:
                logger.info(f"Такой source уже существует!")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении source: {e}")
            return False

async def update_source_changing(source_id, source_name, author_id) -> bool:
    async with async_session() as session:
        source: Source = await session.scalar(select(Source).where(Source.id == source_id))
        if source:
            source.source_name = source_name
            source.author_id = author_id
            await session.commit()
            return True
        else:
            logger.warning(f'Ошибка при изменении источника')
            return False


# добавление слова в базу данных, ничего не возвращает
async def add_word_to_db(word, translation, definition, part, author_id, level, source_id) -> bool:
    async with async_session() as session:
        try:
            word_in_db = await session.scalar(select(Word).where(Word.word == word))
            if not word_in_db:
                session.add(Word(word=word,
                                 translation=translation,
                                 definition=definition,
                                 part=part,
                                 author_id=author_id,
                                 source_id=source_id,
                                 level=level))
                await session.commit()
                logger.info(f"В базу данных добавлено слово {word}!")
            else:
                logger.info(f"Такое слово уже существует!")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении слова: {e}")
            return False


async def update_word_changing(word_id, word, translation, definition, part, author_id, level, source_id) -> bool:
    async with async_session() as session:
        word_in_db : Word = await session.scalar(select(Word).where(Word.id == word_id))
        if word_in_db:
            word_in_db.word = word
            word_in_db.translation = translation
            word_in_db.definition = definition
            word_in_db.part = part
            word_in_db.level = level
            word_in_db.author_id = author_id
            word_in_db.source_id = source_id
            await session.commit()
            return True
        else:
            logger.warning(f'Ошибка при изменении слова')
            return False


# поиск пользователя по фильтрам
async def get_sources_by_filters(source_id: int = None,
                                 source_id_set: set = None,
                                 source_name: str = None):
    async with async_session() as session:
        try:
            selection = select(Source).options(selectinload(Source.words))

            if source_name:
                selection = selection.filter_by(source_name = source_name)

            if source_id_set:
                selection = selection.filter(Source.id.in_(source_id_set)).order_by(Source.created_at.desc())

            rezult = await session.execute(selection)
            sources = rezult.scalars().all()

            if source_id:
                selection = selection.filter(Source.id == source_id)
                rezult = await session.execute(selection)
                sources = rezult.scalars().one_or_none()

            if not sources:
                logger.info(f"не нашел sources в базе данных")
            return sources
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске sources: {e}")


# поиск пользователя по фильтрам
async def get_words_by_filters(word_id: int = None,
                               word_id_set: set = None,
                               word: str = None,
                               limit: int = None,
                               piece_of_word: str = None,
                               word_id_new: int = None,
                               source_id: int = None):
    async with async_session() as session:
        try:
            selection = select(Word).options(selectinload(Word.medias))

            if word_id:
                selection = selection.filter(Word.id == word_id)

            if word_id_set:
                selection = selection.filter(Word.id.in_(word_id_set)).order_by(Word.created_at.asc())

            if source_id:
                selection = selection.filter(Word.source_id == source_id)

            if word:
                selection = selection.filter_by(word = word)

            if piece_of_word:
                selection = selection.filter(Word.word.contains(piece_of_word))

            if limit:
                selection = selection.order_by(Word.id.desc()).limit(limit)

            rezult = await session.execute(selection)
            words = rezult.scalars().all()

            if word_id_new:
                selection = selection.filter(Word.id == word_id_new)
                rezult = await session.execute(selection)
                words = rezult.scalars().one_or_none()

            if not words:
                logger.info(f"не нашел words в базе данных")
            else:
                return words
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске users: {e}")



# запросы по таблице medias
# запрос на медиа с фильтрами
async def get_medias_by_filters(media_id: int = None,
                                media_id_new: int = None,
                                media_id_set: set = None,
                                word_id: int = None,
                                media_type: str = None,
                                word: str = None,
                                telegram_id: str = None,
                                collocation: str = None,
                                test_only: bool = False,
                                media_only: bool = False,
                                limit: int = None,
                                offset: int = None):

    async with async_session() as session:
        try:
            selection = select(Media).options(selectinload(Media.word), selectinload(Media.tasks))

            if media_id:
                selection = selection.filter(Media.id==media_id)

            if media_id_set:
                selection = selection.filter(Media.id.in_(media_id_set)).order_by(Media.created_at.asc())

            if word_id:
                selection = selection.filter_by(word_id=word_id)

            if word:
                selection = selection.join(Word)
                selection = selection.filter(Word.word == word)

            if media_type:
                selection = selection.filter_by(media_type=media_type)

            if telegram_id:
                selection = selection.filter_by(telegram_id=telegram_id)

            if collocation:
                selection = selection.filter(Media.collocation==collocation)

            if test_only:
                selection = selection.filter(Media.media_type.startswith('test'))

            if media_only:
                selection = selection.filter(Media.media_type.startswith('test') == False)

            if offset:
                selection = selection.order_by(Media.id.desc()).offset(limit)

            if limit:
                if offset:
                    selection = selection.order_by(Media.id.desc()).limit(limit).offset(offset)
                else:
                    selection = selection.order_by(Media.id.desc()).limit(limit)



            rez = await session.execute(selection)
            medias = rez.scalars().all()

            if media_id_new:
                selection = selection.filter(Media.id == media_id_new)
                rezult = await session.execute(selection)
                medias = rezult.scalars().one_or_none()

            if medias:
                return medias
            else:
                logger.info(f"не нашел media в базе данных")
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске media: {e}")


# добавление media
async def add_media_to_db(media_type, word_id, collocation, caption, study_day,
                          author_id, telegram_id = None, level = None) -> bool:
    async with async_session() as session:
        try:
            session.add(Media(media_type=media_type,
                              word_id=word_id,
                              collocation=collocation,
                              caption=caption,
                              study_day=study_day,
                              author_id=author_id,
                              telegram_id=telegram_id,
                              level=level))
            await session.commit()
            logger.info(f"В базу данные добавлено медиа с ID {telegram_id}!")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении медиа: {e}")
            return False


# удаление media
async def delete_media_from_db(media_id : int):
    async with async_session() as session:
        try:
            # Сначала находим объект Media по его идентификатору
            media_stmt = select(Media).where(Media.id == media_id)
            result = await session.execute(media_stmt)
            media = result.scalar_one_or_none()

            if media is None:
                raise NoResultFound(f"Медиа с ID {media_id} не найдено.")

            # Удаляем найденный объект
            await session.delete(media)
            await session.commit()
            logger.info(f"Успешно удалили медиа с ID {media_id}.")

        except NoResultFound as e:
            logger.warning(e)
        except SQLAlchemyError as e:
            logger.error(f"Произошла ошибка при удалении медиа: {e}")


# удаление task
async def delete_task_from_db(task_id : int) -> bool:
    async with async_session() as session:
        try:
            # Сначала находим объект Task по его идентификатору
            task_stmt = select(Task).where(Task.id == task_id)
            result = await session.execute(task_stmt)
            task = result.scalar_one_or_none()

            if task is None:
                raise NoResultFound(f"Task с ID {task_id} не найдено.")

            # Удаляем найденный объект
            await session.delete(task)
            await session.commit()
            logger.info(f"Успешно удалил task с ID {task_id}.")
            return True
        except NoResultFound as e:
            logger.warning(e)
            return False
        except SQLAlchemyError as e:
            logger.error(f"Произошла ошибка при удалении task: {e}")
            return False


async def update_media_changing(media_id, media_type, word_id, collocation, caption, study_day,
                                author_id, telegram_id = None, level = None) -> bool:
    async with async_session() as session:
        media : Media = await session.scalar(select(Media).where(Media.id == media_id))
        if media:
            media.media_type = media_type
            media.word_id = word_id
            media.collocation = collocation
            media.caption = caption
            media.study_day = study_day
            media.author_id = author_id
            media.telegram_id = telegram_id
            media.level = level
            await session.commit()
            return True
        else:
            logger.info(f'Ошибка при изменении медиа')
            return False


# запросы по таблице tasks

# добавление task
async def set_task(user_id, media_id, task_time, author_id) -> bool:
    async with async_session() as session:
        try:
            session.add(Task(time=task_time, sent=False, user_id=user_id, media_id=media_id, author_id=author_id))
            await session.commit()
            logger.info(f"В базу данных добавлено задание по {media_id}!")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении слова: {e}")
            return False


#изменение статуса задания на отправлено = да
async def update_task_status(task_id):
    async with (async_session() as session):
        task = await session.scalar(select(Task).where(Task.id == task_id))
        task.sent = True
        await session.commit()


# запрос на задания с фильтрами
async def get_tasks_by_filters(task_id: int = None,
                               task_id_new: int = None,
                               user_id: int = None,
                               user_tg_id : int | BigInteger = None,
                               sent: bool = None,
                               daily_and_missed: bool = False,
                               daily_and_future: bool = False,
                               media_task_only: bool = False):
    async with async_session() as session:
        try:
            selection = select(Task)

            if task_id:
                selection = selection.filter(Task.id==task_id)

            if user_id:
                selection = selection.join(User.tasks)
                selection = selection.filter(Task.user_id==user_id)

            if user_tg_id:
                selection = selection.join(User.tasks)
                selection = selection.filter(User.telegram_id == user_tg_id)

            if sent is not None:
                selection = selection.filter(Task.sent == sent)

            if daily_and_missed:
                end_of_day = datetime.combine(datetime.now().date(), time()) + timedelta(days=1)
                selection = selection.filter(Task.time<end_of_day)

            if daily_and_future:
                start_of_day = datetime.combine(datetime.now().date(), time())
                selection = selection.filter(Task.time>start_of_day).order_by(Task.created_at.desc())

            if media_task_only:
                selection = selection.join(Media)
                selection = selection.filter(Media.media_type.startswith('test') == False)

            selection = selection.options(selectinload(Task.user), selectinload(Task.media))
            rez = await session.execute(selection)
            tasks = rez.scalars().all()

            if task_id_new:
                selection = selection.filter(Task.id == task_id_new)
                selection = selection.options(selectinload(Task.user), selectinload(Task.media))
                rezult = await session.execute(selection)
                tasks = rezult.scalars().one_or_none()

            if tasks:
                return tasks
            else:
                logger.info(f"не нашел tasks в базе данных")

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске заданий: {e}")


async def get_tasks(request_user_id: int = None,
                    request_user_tg_id : int | BigInteger = None,
                    sent: bool = None,
                    media_task_only: bool = None,
                    for_quick_tasks_menu: bool = None):
    async with async_session() as session:
        try:
            selection = select(Task).join(Media)

            if request_user_id:
                selection = selection.filter(Task.user_id == request_user_id)

            if request_user_tg_id:
                # selection =select(User,Task).join(Task,User.tasks_as_user)
                selection = selection.join(User, Task.user_id == User.id)
                selection = selection.filter(User.telegram_id == request_user_tg_id).order_by(Task.time.desc())

            if sent is not None:
                selection = selection.filter(Task.sent == sent)

            if media_task_only:
                selection = selection.filter(~Media.media_type.startswith('test'))

            if for_quick_tasks_menu:
                selection = selection.filter(Task.sent == False)
                today_start = datetime.combine(date.today(), datetime.min.time())  # Начало текущего дня
                tomorrow_start = today_start + timedelta(days=1)
                selection = selection.filter(Task.time < tomorrow_start)
                selection = selection.filter(Media.media_type.startswith('test') == False)



            selection = selection.options(selectinload(Task.user),
                                          selectinload(Task.media).selectinload(Media.word).selectinload(Word.source))
            rez = await session.execute(selection)
            tasks = rez.scalars().all()
            if tasks:
                return tasks
            else:
                logger.info(f"не нашел tasks в базе данных")

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске заданий: {e}")


# добавление task
async def set_homework(hometask, users, homework_date, author_id) -> bool:
    async with async_session() as session:
        try:
            session.add(Homework(hometask=hometask, users=users, time=homework_date, author_id=author_id))
            await session.commit()
            logger.info(f"В базу данных добавлено домашнее задание задание  {hometask}!")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении домашнего задания в базу данных: {e}")
            return False

async def update_homework_editing(homework_id, hometask, users, homework_date, author_id) -> bool:
    async with (async_session() as session):
        homework : Homework = await session.scalar(select(Homework).where(Homework.id == homework_id))
        if homework:
            homework.hometask = hometask
            homework.users = users
            homework.time = homework_date
            homework.author_id = author_id
            await session.commit()
            return True
        else:
            logger.info(f'Ошибка при изменении домашнего задания')
            return False


# запрос на задания с фильтрами
async def get_homeworks_by_filters(homework_id: int = None,
                                   homework_id_new: int = None,
                                   actual : bool = True):
    async with async_session() as session:
        try:
            selection = select(Homework)

            if homework_id:
                selection = selection.filter(Homework.id==homework_id)

            if actual:
                selection = selection.filter(Homework.time > datetime.now())

            rez = await session.execute(selection)
            homeworks = rez.scalars().all()

            if homework_id_new:
                selection = selection.filter(Homework.id == homework_id_new)
                # selection = selection.options(selectinload(Task.user), selectinload(Task.media))
                rezult = await session.execute(selection)
                homeworks = rezult.scalars().one_or_none()

            if homeworks:
                return homeworks
            else:
                logger.info(f"не нашел homeworks в базе данных")

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске homeworks: {e}")

# добавление url
async def set_link(link_name, link_url, users, priority) -> bool:
    async with async_session() as session:
        try:
            session.add(Link(name=link_name, link=link_url, users=users, priority=priority))
            await session.commit()
            logger.info(f"В базу данных добавлена ссылка {link_url}!")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении ссылки в базу данных: {e}")
            return False

async def update_link_changing(link_id, link_name, link_url, users, priority) -> bool:
    async with async_session() as session:
        link : Link = await session.scalar(select(Link).where(Link.id == link_id))
        if link:
            link.name = link_name
            link.link = link_url
            link.users = users
            link.priority = priority
            await session.commit()
            return True
        else:
            logger.info(f'Ошибка при изменении ссылки')
            return False


# запрос на задания с фильтрами
async def get_links_by_filters(link_id :int = None, user_id: int = None):
    async with async_session() as session:
        try:
            selection = select(Link)

            if user_id:
                selection = selection.filter(Link.users.contains(user_id)).order_by(Link.priority.asc(), Link.created_at.desc())
                # selection = selection.filter(func.find_in_set(str(user_id), Link.users) > 0).order_by(Link.priority.asc(), Link.created_at.desc())

            rez = await session.execute(selection)
            links = rez.scalars().all()

            if link_id:
                selection = selection.filter(Link.id == link_id)
                rez = await session.execute(selection)
                links = rez.scalars().one_or_none()

            if links:
                return links
            else:
                logger.info(f"не нашел links в базе данных")

            return links

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске заданий: {e}")




# добавление group
async def set_group(name: str, users: str, level: str) -> bool:
    async with async_session() as session:
        try:
            session.add(Group(name=name, users=users, level=level))
            await session.commit()
            logger.info(f"В базу данных добавлена группа {users} - {name}!")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении группы в базу данных: {e}")
            return False


async def update_group_editing(group_id: int, name: str, users: str, level: str) -> bool:
    async with async_session() as session:
        group: Group = await session.scalar(select(Group).where(Group.id == group_id))
        if group:
            group.name = name
            group.users = users
            group.level = level
            await session.commit()
            return True
        else:
            logger.warning(f"не найдена группа для изменения")
            return False


# поиск пользователя по фильтрам
async def get_groups_by_filters(name: str = None,
                                group_id: int  = None,
                                limit: int = 30):
    async with async_session() as session:
        try:
            selection = select(Group)

            if name:
                selection = selection.filter_by(name = name)

            if limit:
                selection = selection.order_by(Group.id.desc()).limit(limit)

            rezult = await session.execute(selection)
            groups = rezult.scalars().all()

            if group_id:
                selection = selection.filter_by(id = group_id)
                rezult = await session.execute(selection)
                groups = rezult.scalars().one_or_none()

            return groups
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске groups: {e}")