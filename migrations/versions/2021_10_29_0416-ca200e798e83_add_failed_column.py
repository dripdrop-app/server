"""add failed column

Revision ID: ca200e798e83
Revises: e03692bc831d
Create Date: 2021-10-29 04:16:05.219135

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ca200e798e83"
down_revision = "e03692bc831d"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("music_jobs", sa.Column("failed", sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("music_jobs", "failed")
    # ### end Alembic commands ###
