"""add med-tasks forkey with del and default user intervals

Revision ID: 2a51c1df652e
Revises: 99ece2ef9276
Create Date: 2025-05-03 00:53:24.340223

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a51c1df652e'
down_revision: Union[str, None] = '99ece2ef9276'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('intervals', server_default="10:00,14:00")
    # 2
    with op.batch_alter_table('tasks') as batch_op:
        batch_op.create_foreign_key(
            constraint_name='fk_media-tasks',
            referent_table='medias',
            local_cols=['media_id'],
            remote_cols=['id'],
            ondelete='CASCADE'
        )


def downgrade() -> None:
    # 1
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('intervals', server_default="10:00-11:00,14:00-15:00")
    # 2
    with op.batch_alter_table('tasks') as batch_op:
        batch_op.drop_constraint(constraint_name='fk_media-tasks', type_='foreignkey')
