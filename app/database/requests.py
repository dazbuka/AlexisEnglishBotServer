from sqlalchemy.orm import selectinload, joinedload, lazyload, subqueryload
from sqlalchemy import BigInteger
from config import bot, DEVELOPER_ID
from app.database.models import async_session, Homework
from app.database.models import User, Task, Media, Word
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from config import logger
from datetime import timedelta, datetime, time
from aiogram.types import Message


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
        if user:
            if user.last_message_id:
                last_msg = user.last_message_id
                return last_msg
        else:
            logger.info(f"Ошибка! Не могу определить номер последнего сообщения для {user_tg_id}")


# поиск пользователя по фильтрам
async def get_users_by_filters(user_id: int = None,
                               user_tg_id: int | BigInteger  = None,
                               limit: int = 30):
    async with async_session() as session:
        try:
            selection = select(User).options(selectinload(User.tasks))

            if user_id:
                selection = selection.filter_by(id = user_id)

            if user_tg_id:
                selection = selection.filter_by(telegram_id = user_tg_id)

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

# запросы по таблице words

# добавление слова в базу данных, ничего не возвращает
async def add_word_to_db(word, translation, definition, part, author_id, level) -> bool:
    async with async_session() as session:
        try:
            word_in_db = await session.scalar(select(Word).where(Word.word == word))
            if not word_in_db:
                session.add(Word(word=word,
                                 translation=translation,
                                 definition=definition,
                                 part=part,
                                 author_id=author_id,
                                 level=level))
                await session.commit()
                logger.info(f"В базу данных добавлено слово {word}!")
            else:
                logger.info(f"Такое слово уже существует!")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении слова: {e}")
            return False

# поиск пользователя по фильтрам
async def get_words_by_filters(word_id: int = None,
                               word: str = None,
                               part: str = None,
                               limit: int = None,
                               piece_of_word: str = None):
    async with async_session() as session:
        try:
            selection = select(Word).options(selectinload(Word.medias))

            if word_id:
                selection = selection.filter(Word.id == word_id)

            if word:
                selection = selection.filter_by(word = word)

            if piece_of_word:
                selection = selection.filter(Word.word.contains(piece_of_word))

            if part:
                selection = selection.filter_by(part = part)

            if limit:
                selection = selection.order_by(Word.id.desc()).limit(limit)

            rezult = await session.execute(selection)
            words = rezult.scalars().all()

            if not words:
                logger.info(f"не нашел words в базе данных")
            else:
                return words
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске users: {e}")



# запросы по таблице medias
# запрос на медиа с фильтрами
async def get_medias_by_filters(media_id: int = None,
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
                               user_id: int = None,
                               user_tg_id : int | BigInteger = None,
                               sent: bool = None,
                               daily_tasks_only: bool = False,
                               missed_tasks_only: bool = False,
                               future_tasks_only: bool = False,
                               num_limit: int = 0,
                               media_task_only: bool = False,
                               limit: int = None,
                               offset: int = None):
    async with async_session() as session:
        try:
            selection = select(Task)

            if task_id:
                selection = selection.filter(Task.id==task_id)

            if user_id:
                selection = selection.filter(Task.user_id==user_id)

            if user_tg_id:
                # selection =select(User,Task).join(Task,User.tasks_as_user)
                selection = selection.join(User.tasks)
                selection = selection.filter(User.telegram_id == user_tg_id)

            if sent is not None:
                selection = selection.filter(Task.sent == sent)

            if daily_tasks_only:
                beg_of_day = datetime.combine(datetime.now().date(), time())
                end_of_day = beg_of_day + timedelta(days=1)
                selection = selection.filter(Task.time>beg_of_day, Task.time<end_of_day)

            if missed_tasks_only:
                beg_of_day = datetime.combine(datetime.now().date(), time())
                selection = selection.filter(Task.time < beg_of_day)

            if future_tasks_only:
                end_of_day = datetime.combine(datetime.now().date(), time()) + timedelta(days=1)
                selection = selection.filter(Task.time>end_of_day)

            if limit:
                if offset:
                    selection = selection.order_by(Task.id.desc()).limit(limit).offset(offset)
                else:
                    selection = selection.order_by(Task.id.desc()).limit(limit)

            if num_limit:
                if num_limit != 0:
                    selection = selection.limit(num_limit)

            if media_task_only:
                selection = selection.join(Media)
                selection = selection.filter(Media.media_type.startswith('test') == False)

            # if test_only:
            #     selection = selection.filter(Media.media_type.startswith('test'))
            #
            # if media_only:
            #     selection = selection.filter(Media.media_type.startswith('test') == False)

            selection = selection.options(selectinload(Task.user), selectinload(Task.media))
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


# запрос на задания с фильтрами
async def get_homeworks_by_filters(homework_id: int = None,
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

            if homeworks:
                return homeworks
            else:
                logger.info(f"не нашел homeworks в базе данных")

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске homeworks: {e}")