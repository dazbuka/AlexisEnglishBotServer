import enum
from typing import List
from sqlalchemy import func, BigInteger, Integer, String, ForeignKey, DateTime, TIMESTAMP, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from config import DB_URL
from datetime import datetime

# Создание асинхронного движка для подключения к БД и фабрики сессий
engine = create_async_engine(DB_URL)
async_session = async_sessionmaker(engine)

# Родительский классс для всех таблиц
class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    # Общее поле "id" для всех таблиц
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Поля времени создания и обновления записи
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class UserStatus(str, enum.Enum):
    ACTIVE = 'ACTIVE'
    BLOCKED = 'BLOCKED'
    DELETED = 'DELETED'
    WAITING = 'WAITING'

class User(Base):
    __tablename__ = 'users'

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str | None]
    intervals: Mapped[str | None] = mapped_column(server_default="10:00-11:00,14:00-15:00")
    ident_name: Mapped[str] = mapped_column(unique=True)
    status: Mapped[UserStatus] = mapped_column(server_default=UserStatus.BLOCKED)
    last_message_id: Mapped[int | None]

    tasks: Mapped[list['Task']] = relationship("Task", back_populates="user", cascade="all, delete-orphan")

    words: Mapped[List['Word']] = relationship("Word", back_populates="author")
    medias: Mapped[List['Media']] = relationship("Media", back_populates="author")
    events: Mapped[List['Event']] = relationship("Event", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, name='{self.ident_name}')>"


class Group(Base):
    __tablename__ = 'groups'

    name: Mapped[str] = mapped_column(unique=True)
    users: Mapped[str]
    level: Mapped[int]

    def __repr__(self):
        return f"<Group (group={self.name}, users={self.users}, level={self.level})>"


class Link(Base):
    __tablename__ = 'links'

    name: Mapped[str] = mapped_column(unique=True)
    link: Mapped[str]
    users: Mapped[str] = mapped_column(nullable=True)
    priority: Mapped[int] = mapped_column(nullable=True)

    def __repr__(self):
        return f"<Link (name={self.name}, priority={self.priority}, link={self.link}, users={self.users})>"


class Task(Base):
    __tablename__ = 'tasks'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    media_id: Mapped[int] = mapped_column(ForeignKey('medias.id'))
    time: Mapped[datetime] = mapped_column(DateTime)
    sent: Mapped[bool] = mapped_column(server_default='False')

    author_id: Mapped[int] #= mapped_column(ForeignKey('users.id'))

    user: Mapped["User"] = relationship("User", back_populates="tasks", foreign_keys=[user_id])
    media: Mapped["Media"] = relationship("Media", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, user_id={self.user_id}, media_id={self.media_id}, sent={self.sent})>"



class Media(Base):
    __tablename__ = 'medias'

    media_type: Mapped[str]
    word_id: Mapped[int] = mapped_column(ForeignKey('words.id'))
    collocation: Mapped[str | None]
    caption: Mapped[str | None] = mapped_column(Text)
    telegram_id: Mapped[str | None]
    study_day: Mapped[int | None]
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    level: Mapped[str | None]

    author: Mapped["User"] = relationship("User", back_populates="medias")
    word: Mapped["Word"] = relationship("Word", back_populates="medias")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="media")

    def __repr__(self):
        return f"<Media(id={self.id}, word_id={self.word_id}, collocation={self.collocation})>"



class Word(Base):
    __tablename__ = 'words'

    word: Mapped[str] = mapped_column(unique=True)
    definition: Mapped[str | None]
    translation: Mapped[str | None]
    part: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    level: Mapped[str | None]

    author: Mapped["User"] = relationship("User", back_populates="words")
    medias: Mapped[List["Media"]] = relationship("Media", back_populates="word", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Word(id={self.id}, word={self.word})>"


class Homework(Base):
    __tablename__ = 'homeworks'

    hometask: Mapped[str]
    time: Mapped[datetime] = mapped_column(DateTime)
    author_id: Mapped[int]
    users: Mapped[str]

    def __repr__(self):
        return f"<Homework (hometask={self.hometask}, time={self.time}, users={self.users})>"


class EventTypeEnum(str, enum.Enum):
    ADDING='добавление'
    GETTING='получение'
    OTHER='иное'


class Event(Base):
    __tablename__ = 'events'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    type: Mapped[EventTypeEnum] = mapped_column(default=EventTypeEnum.OTHER)
    action: Mapped[str | None]

    user: Mapped["User"] = relationship("User", back_populates="events")

    def __repr__(self):
        return f"<Event(id={self.id}, user_id={self.user_id}, type={self.type}, action={self.action})>"


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)