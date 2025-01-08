"""add liked youtube videos

Revision ID: 34aca6fbef27
Revises: 6f73ab459616
Create Date: 2022-04-15 17:09:34.832851

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "34aca6fbef27"
down_revision = "6f73ab459616"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "youtube_video_likes",
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("video_id", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["email"],
            ["google_accounts.email"],
            name="youtube_video_likes_email_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["video_id"],
            ["youtube_videos.id"],
            name="youtube_video_likes_video_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("email", "video_id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("youtube_video_likes")
    # ### end Alembic commands ###
