"""empty message

Revision ID: 410678c9c20a
Revises: f86cb34cc617
Create Date: 2024-03-04 17:08:08.381911

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '410678c9c20a'
down_revision = 'f86cb34cc617'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.drop_column('league_name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.add_column(sa.Column('league_name', sa.VARCHAR(), nullable=True))

    # ### end Alembic commands ###