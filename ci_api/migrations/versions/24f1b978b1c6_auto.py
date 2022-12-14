"""auto

Revision ID: 24f1b978b1c6
Revises: ca9a72534901
Create Date: 2022-12-07 09:26:56.138638

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = '24f1b978b1c6'
down_revision = 'ca9a72534901'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('payment_checks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payment_checks_id'), 'payment_checks', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_payment_checks_id'), table_name='payment_checks')
    op.drop_table('payment_checks')
    # ### end Alembic commands ###