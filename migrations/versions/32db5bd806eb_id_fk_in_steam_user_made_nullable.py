"""id fk in steam_user made nullable

Revision ID: 32db5bd806eb
Revises: 1ee195fdf684
Create Date: 2025-05-10 19:47:04.476550

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '32db5bd806eb'
down_revision = '1ee195fdf684'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('steam_user', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('steam_user', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
