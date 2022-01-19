"""change expires to integer

Revision ID: 2426dbe78bbd
Revises: d2ca34743868
Create Date: 2021-12-30 18:34:27.893232

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2426dbe78bbd'
down_revision = 'd2ca34743868'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('google_accounts', 'expires', type_=sa.Integer)
    pass
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('google_accounts', 'expires', type_=sa.Numeric)
    pass
    # ### end Alembic commands ###