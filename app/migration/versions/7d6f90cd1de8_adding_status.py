"""adding status

Revision ID: 7d6f90cd1de8
Revises: bc6ee0b84ac5
Create Date: 2025-02-26 20:54:11.274833

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d6f90cd1de8'
down_revision: Union[str, None] = 'bc6ee0b84ac5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('status', server_default='BLOCKED')

def downgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('status', server_default='ACTIVE')
