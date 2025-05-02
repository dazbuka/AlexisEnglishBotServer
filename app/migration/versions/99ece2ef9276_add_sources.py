"""add sources

Revision ID: 99ece2ef9276
Revises: 7eae63f37061
Create Date: 2025-04-25 10:09:52.644752

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99ece2ef9276'
down_revision: Union[str, None] = '7eae63f37061'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1
    op.create_table('sources',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('author_id', sa.Integer(), nullable=True),
                    sa.Column('source_name', sa.String, nullable=False),
                    sa.Column('source_type', sa.String, nullable=True),
                    sa.Column('source_description', sa.String, nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(),
                              nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.now(),
                              nullable=False, onupdate=sa.func.now()),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('source_name'),
                    sa.ForeignKeyConstraint(['author_id'], ['users.id']))
    # 2
    with op.batch_alter_table('words') as batch_op:
        batch_op.add_column(sa.Column('source_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_words_source', 'sources', ['source_id'], ['id'])


def downgrade() -> None:
    # 2
    with op.batch_alter_table('words') as batch_op:
        batch_op.drop_constraint('fk_words_source', type_='foreignkey')
        batch_op.drop_column('source_id')
    # 1
    op.drop_table('sources')

