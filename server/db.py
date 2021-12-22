import databases
import sqlalchemy
from sqlalchemy.sql.expression import text
from server.config import DATABASE_URL

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column("username", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("password", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("admin", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column("approved", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column(
        "created_at", sqlalchemy.dialects.postgresql.TIMESTAMP, server_default=text("NOW()")),
)

google_accounts = sqlalchemy.Table(
    'google_accounts',
    metadata,
    sqlalchemy.Column("email", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("access_token", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("refresh_token", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("expires", sqlalchemy.Numeric, nullable=False),
    sqlalchemy.Column(
        "created_at", sqlalchemy.dialects.postgresql.TIMESTAMP, server_default=text("NOW()"))
)

youtube_jobs = sqlalchemy.Table(
    'youtube_jobs',
    metadata,
    sqlalchemy.Column("job_id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.ForeignKey(
        google_accounts.c.email), nullable=False),
    sqlalchemy.Column("completed", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column(
        "created_at", sqlalchemy.dialects.postgresql.TIMESTAMP, server_default=text("NOW()"))
)

music_jobs = sqlalchemy.Table(
    'music_jobs',
    metadata,
    sqlalchemy.Column("job_id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.ForeignKey(
        users.c.username), nullable=False),
    sqlalchemy.Column("filename", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("youtube_url", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("artwork_url", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("artist", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("album", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("grouping", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("completed", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column("failed", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.dialects.postgresql.TIMESTAMP,
                      server_default=text("NOW()"))
)


sessions = sqlalchemy.Table(
    'sessions',
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.ForeignKey(
        users.c.username), nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.dialects.postgresql.TIMESTAMP,
                      server_default=text("NOW()"))
)
