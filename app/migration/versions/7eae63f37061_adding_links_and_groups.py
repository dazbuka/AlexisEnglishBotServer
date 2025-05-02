"""adding links and groups

Revision ID: 7eae63f37061
Revises: 7d6f90cd1de8
Create Date: 2025-03-02 20:37:39.414082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7eae63f37061'
down_revision: Union[str, None] = '7d6f90cd1de8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
