"""add job start time

Revision ID: e03692bc831d
Revises: 7e43a80afadb
Create Date: 2021-10-29 01:40:51.659133

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e03692bc831d"
down_revision = "7e43a80afadb"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "music_jobs",
        sa.Column(
            "started",
            postgresql.TIMESTAMP(),
            server_default=sa.text("NOW()"),
            nullable=True,
        ),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("music_jobs", "started")
    # ### end Alembic commands ###
