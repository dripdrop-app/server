"""add default values on datetimes

Revision ID: c0ec00254dca
Revises: 51112a4dba95
Create Date: 2022-07-31 18:14:02.484510

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "c0ec00254dca"
down_revision = "51112a4dba95"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    connection = op.get_bind()
    connection.execute("UPDATE google_accounts SET last_updated = NOW() WHERE TRUE;")
    op.alter_column(
        "google_accounts",
        "last_updated",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        existing_server_default=sa.text("now()"),
    )
    op.alter_column(
        "youtube_channels",
        "last_updated",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        existing_server_default=sa.text("now()"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "youtube_channels",
        "last_updated",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
        existing_server_default=sa.text("now()"),
    )
    op.alter_column(
        "google_accounts",
        "last_updated",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
        existing_server_default=sa.text("now()"),
    )
    # ### end Alembic commands ###
