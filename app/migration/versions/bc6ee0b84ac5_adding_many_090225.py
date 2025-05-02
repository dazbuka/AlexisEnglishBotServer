"""adding many 090225

Revision ID: bc6ee0b84ac5
Revises: 593ca5f77dc4
Create Date: 2025-02-09 22:39:58.527764

"""
from typing import Sequence, Union
from sqlalchemy import Enum
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc6ee0b84ac5'
down_revision: Union[str, None] = '593ca5f77dc4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None




def update_ident_name():
    connection = op.get_bind()
    # Получаем все записи из таблицы users
    users = connection.execute(sa.text("SELECT id, username, first_name, last_name FROM users")).fetchall()

    for user in users:
        # Формируем строку для нового поля
        str1 = f'{user.username} ({user.first_name}'
        str2 = f' {user.last_name})' if user.last_name!=None else ')'
        ident = str1+str2
        # Обновляем запись в базе данных
        connection.execute(sa.text(f"UPDATE users SET ident_name = :value WHERE id = :id"),
                           {"value": ident, "id": user.id})

def update_task_author():
    connection = op.get_bind()
    tasks = connection.execute(sa.text("SELECT * FROM tasks")).fetchall()
    for task in tasks:
        # Обновляем запись в базе данных
        connection.execute(sa.text(f"UPDATE tasks SET author_id = :value WHERE id = :id"),
                           {"value": 2, "id": task.id})

def update_task_sent():
    connection = op.get_bind()
    tasks = connection.execute(sa.text("SELECT id, sended FROM tasks")).fetchall()
    for task in tasks:
        sent = True if task.sended == 'yes' else False
        connection.execute(sa.text(f"UPDATE tasks SET sent = :value WHERE id = :id"),
                           {"value": sent, "id": task.id})

def update_task_sended():
    connection = op.get_bind()
    tasks = connection.execute(sa.text("SELECT id, sent FROM tasks")).fetchall()
    for task in tasks:
        sended = 'yes' if task.sent == True else 'no'
        connection.execute(sa.text(f"UPDATE tasks SET sended = :value WHERE id = :id"),
                           {"value": sended, "id": task.id})



def upgrade() -> None:
    # Добавляем новое поле 'ident_name' в таблицу 'users'
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('ident_name', sa.String(), nullable=True))

    update_ident_name()

    with op.batch_alter_table('tasks') as batch_op:
        batch_op.add_column(sa.Column('author_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sent', sa.Boolean(), nullable=True))

    update_task_author()
    update_task_sent()



    # Делаем поле 'ident_name' не null
    with op.batch_alter_table('users') as batch_op:
        # 1
        batch_op.alter_column('ident_name', nullable=False)
        batch_op.create_unique_constraint('uk_ident_name', ['ident_name'])
        # 2
        batch_op.alter_column('telegram_id', existing_type=sa.Integer(), type_=sa.BigInteger(), existing_nullable=False)
        # 3
        batch_op.alter_column('username', existing_nullable=True, nullable=False)
        # 4
        batch_op.alter_column('first_name', existing_nullable=True, nullable=False)
        # 5
        batch_op.alter_column('timedelta', new_column_name='last_message_id')
        # 6
        batch_op.add_column(sa.Column('intervals', sa.String(), nullable=True,
                                      server_default="10:00-11:00,14:00-15:00"))
        # 7
        StatusEnum = Enum('ACTIVE', 'BLOCKED')
        batch_op.add_column(sa.Column('status', StatusEnum, nullable=False, server_default='ACTIVE'))

        # batch_op.add_column(sa.Column('status', sa.Enum('ACTIVE', 'BLOCKED', name='UserStatus'),
        #                                nullable=False, server_default='active'))

        # 8
        batch_op.alter_column('id', existing_type=sa.TEXT(), type_=sa.Integer(), autoincrement=True)




    # Делаем поле 'ident_name' не null
    with op.batch_alter_table('tasks') as batch_op:
        # 1
        batch_op.alter_column('author_id', nullable=False)
        batch_op.create_foreign_key('fk_tasks_author',
                                    referent_table='users',
                                    local_cols=['author_id'],
                                    remote_cols=['id'])
        # 2
        batch_op.alter_column('sent', nullable=False, server_default='False')
        # 3
        batch_op.drop_column('sended')







    with op.batch_alter_table('medias') as batch_op:
        # 1
        batch_op.alter_column('media_type', existing_nullable=True, nullable=False)
        # 2
        batch_op.alter_column('caption', existing_type=sa.String(), type_=sa.Text(), nullable=True)



  # Делаем поле 'ident_name' не null
    with op.batch_alter_table('words') as batch_op:
        # 1
        batch_op.alter_column('word', existing_nullable=True, nullable=False)
        batch_op.create_unique_constraint('uk_word', ['word'])
        # 2
        batch_op.alter_column('part', existing_nullable=True, nullable=False)

    op.create_table('homeworks',
                    sa.Column('id', sa.Integer(), nullable=False),
                             sa.Column('hometask', sa.String, nullable=False),
                             sa.Column('time', sa.DateTime(), nullable=False),
                             sa.Column('author_id', sa.Integer(), nullable=True),
                             sa.Column('users', sa.String(), nullable=False),
                             sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(),
                                       nullable=False),
                             sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.now(),
                                       nullable=False, onupdate=sa.func.now()),
                             sa.PrimaryKeyConstraint('id')
                    )


def downgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        # 1
        batch_op.drop_column('ident_name')
        # 2
        batch_op.alter_column('telegram_id', existing_type=sa.BigInteger(), type_=sa.Integer())
        # 3
        batch_op.alter_column('username', existing_nullable=False, nullable=True)
        # 4
        batch_op.alter_column('first_name', existing_nullable=False, nullable=True)
        # 5
        batch_op.alter_column('last_message_id', new_column_name='timedelta')
        # 6
        batch_op.drop_column('intervals')
        # 7
        batch_op.drop_column('status')
        # 8
        batch_op.alter_column('id', existing_type=sa.Integer(), type_=sa.TEXT(), autoincrement=True)


    with op.batch_alter_table('tasks') as batch_op:
        batch_op.add_column(sa.Column('sended', sa.Boolean(), nullable=True))

    update_task_sended()

    with op.batch_alter_table('tasks') as batch_op:
        # 1
        batch_op.drop_column('author_id')
        batch_op.drop_constraint('fk_tasks_author', type_='foreignkey')

        # 2
        batch_op.alter_column('sended', nullable=False, server_default='no')
        # 3
        batch_op.drop_column('sent')


    with op.batch_alter_table('medias') as batch_op:
        # 1
        batch_op.alter_column('media_type', existing_nullable=False, nullable=True)
        # 2
        batch_op.alter_column('caption', existing_type=sa.Text(), type_=sa.String(), nullable=True)


    # Делаем поле 'ident_name' не null
    with op.batch_alter_table('words') as batch_op:
        # 1
        batch_op.alter_column('word', existing_nullable=False, nullable=True)
        batch_op.drop_constraint('uk_word')
        # 2
        batch_op.alter_column('part', existing_nullable=False, nullable=True)

    op.drop_table('homeworks')