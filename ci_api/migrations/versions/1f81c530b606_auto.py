"""auto

Revision ID: 1f81c530b606
Revises: eb1e0c9dc5d1
Create Date: 2022-12-14 13:39:00.619852

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = '1f81c530b606'
down_revision = 'eb1e0c9dc5d1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('is_email_verified', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('push_token', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'push_token')
    op.drop_column('users', 'is_email_verified')
    # ### end Alembic commands ###