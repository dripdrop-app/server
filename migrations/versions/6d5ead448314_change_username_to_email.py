"""change username to email

Revision ID: 6d5ead448314
Revises: 809e4c2067cc
Create Date: 2021-12-21 21:12:05.646506

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d5ead448314'
down_revision = '809e4c2067cc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'username', new_column_name='email')
    op.add_column('google_accounts', sa.Column(
        'user_email', sa.String(), nullable=False))
    op.create_foreign_key(None, 'google_accounts', 'users', [
                          'user_email'], ['email'])
    op.alter_column('sessions', 'username', new_column_name='user_email')
    op.alter_column('music_jobs', 'username', new_column_name='user_email')
    op.drop_column('youtube_jobs', 'completed')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('youtube_jobs', sa.Column(
        'completed', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.alter_column('users', 'email', new_column_name='username')
    op.alter_column('sessions', 'user_email', new_column_name='username')
    op.alter_column('music_jobs', 'user_email', new_column_name='username')
    op.drop_constraint(None, 'google_accounts', type_='foreignkey')
    op.drop_column('google_accounts', 'user_email')
    # ### end Alembic commands ###