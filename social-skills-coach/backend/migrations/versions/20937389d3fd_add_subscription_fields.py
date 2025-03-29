"""add subscription fields

Revision ID: 20937389d3fd
Revises: 
Create Date: 2025-03-28 19:59:49.920675

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20937389d3fd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('conversations', schema=None) as batch_op:
        batch_op.alter_column('timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('stripe_customer_id', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('subscription_id', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('subscription_status', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('tier', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('scenarios_accessed', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('last_reset', sa.Date(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('last_reset')
        batch_op.drop_column('scenarios_accessed')
        batch_op.drop_column('tier')
        batch_op.drop_column('subscription_status')
        batch_op.drop_column('subscription_id')
        batch_op.drop_column('stripe_customer_id')

    with op.batch_alter_table('conversations', schema=None) as batch_op:
        batch_op.alter_column('timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)

    # ### end Alembic commands ### 