"""remove approved from accounts

Revision ID: 2116822569db
Revises: ea36c1c869ae
Create Date: 2022-07-17 22:43:34.985411

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2116822569db"
down_revision = "ea36c1c869ae"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "approved")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users",
        sa.Column("approved", sa.BOOLEAN(), autoincrement=False, nullable=False),
    )
    # ### end Alembic commands ###
