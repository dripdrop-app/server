"""add user_submitted field to youtube subscriptions

Revision ID: df6a1da1693c
Revises: 58d29fd76d19
Create Date: 2023-03-08 06:50:29.327382

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "df6a1da1693c"
down_revision = "58d29fd76d19"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "youtube_subscriptions",
        sa.Column("user_submitted", sa.Boolean(), nullable=True),
    )
    op.execute("UPDATE youtube_subscriptions SET user_submitted = 'FALSE'")
    op.alter_column("youtube_subscriptions", "user_submitted", nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("youtube_subscriptions", "user_submitted")
    # ### end Alembic commands ###
