"""Added Drive DB

Revision ID: dd7cbe3bd5fe
Revises: 2e9474476a8a
Create Date: 2020-07-15 16:24:18.269937

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd7cbe3bd5fe'
down_revision = '2e9474476a8a'
branch_labels = None
depends_on = None
def upgrade():
    op.create_table('drives',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=999), nullable=True),
    sa.Column('path', sa.String(length=999), nullable=False),
    sa.Column('size', sa.Integer(), nullable=False),
    sa.Column('free_space', sa.Integer(), nullable=True),
    sa.Column('mounted', sa.Boolean(), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=False),
    sa.Column('last_used', sa.DateTime(), nullable=True), 
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('drivelog',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('drive_id', sa.Integer()),
    sa.Column('action', sa.String(length=255), nullable=False),
    sa.Column('user', sa.String(length=255), nullable=False),
    sa.Column('action_date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['drive_id'], ['drives.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint(id)
    )
def downgrade():
    pass
