"""add youtube video queue

Revision ID: 113fddd62ffa
Revises: 34aca6fbef27
Create Date: 2022-04-30 17:44:51.711407

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "113fddd62ffa"
down_revision = "34aca6fbef27"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "youtube_video_queues",
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
            name="youtube_video_queues_email_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["video_id"],
            ["youtube_videos.id"],
            name="youtube_video_queues_video_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("email", "video_id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("youtube_video_queues")
    # ### end Alembic commands ###