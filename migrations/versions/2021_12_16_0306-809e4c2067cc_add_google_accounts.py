"""add google accounts

Revision ID: 809e4c2067cc
Revises: 7c36d6ca112e
Create Date: 2021-12-16 03:06:38.118862

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "809e4c2067cc"
down_revision = "7c36d6ca112e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "google_accounts",
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("access_token", sa.String(), nullable=False),
        sa.Column("refresh_token", sa.String(), nullable=False),
        sa.Column("expires", sa.Numeric(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("NOW()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("email"),
    )
    op.create_table(
        "youtube_jobs",
        sa.Column("job_id", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("NOW()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["email"],
            ["google_accounts.email"],
        ),
        sa.PrimaryKeyConstraint("job_id"),
    )
    op.add_column(
        "music_jobs",
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("NOW()"),
            nullable=True,
        ),
    )
    op.drop_column("music_jobs", "started")
    op.add_column(
        "sessions",
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("NOW()"),
            nullable=True,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("NOW()"),
            nullable=True,
        ),
    )
    op.drop_column("users", "createdAt")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users",
        sa.Column(
            "createdAt",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_column("users", "created_at")
    op.drop_column("sessions", "created_at")
    op.add_column(
        "music_jobs",
        sa.Column(
            "started",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_column("music_jobs", "created_at")
    op.drop_table("youtube_jobs")
    op.drop_table("google_accounts")
    # ### end Alembic commands ###
