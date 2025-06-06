"""correction models

Revision ID: b30abe32fccb
Revises: f39651e7a56f
Create Date: 2025-06-05 21:14:01.100716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b30abe32fccb'
down_revision: Union[str, None] = 'f39651e7a56f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('books', sa.Column('appended_at', sa.DateTime(), nullable=False))
    op.add_column('books', sa.Column('reader_id', sa.Integer(), nullable=True))
    op.alter_column('books', 'ISBN',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.create_foreign_key(None, 'books', 'users', ['reader_id'], ['id'])
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'created_at')
    op.drop_constraint(None, 'books', type_='foreignkey')
    op.alter_column('books', 'ISBN',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('books', 'reader_id')
    op.drop_column('books', 'appended_at')
    # ### end Alembic commands ###
