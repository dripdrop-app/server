"""change music job id to just id

Revision ID: 68a57d37fad0
Revises: 6d5ead448314
Create Date: 2021-12-21 21:32:10.263822

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "68a57d37fad0"
down_revision = "6d5ead448314"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("music_jobs", "job_id", new_column_name="id")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("music_jobs", "id", new_column_name="job_id")
    # ### end Alembic commands ###
