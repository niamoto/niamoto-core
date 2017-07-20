"""Add fact_table_registry table

Revision ID: c017cc9221b0
Revises: 831d427c8a18
Create Date: 2017-07-20 17:30:13.699268

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c017cc9221b0'
down_revision = '831d427c8a18'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('fact_table_registry',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('date_create', sa.DateTime(), nullable=False),
        sa.Column('date_update', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name=op.f('uq_fact_table_registry_name')),
        schema='niamoto'
    )


def downgrade():
    op.drop_table('fact_table_registry', schema='niamoto')