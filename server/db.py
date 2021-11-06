import databases
import sqlalchemy
from sqlalchemy.sql.expression import text
from server.config import DATABASE_URL

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

music_jobs = sqlalchemy.Table(
    'music_jobs',
    metadata,
    sqlalchemy.Column("job_id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("filename", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("youtube_url", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("artwork_url", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("artist", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("album", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("grouping", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("completed", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column("failed", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column("started", sqlalchemy.dialects.postgresql.TIMESTAMP,
                      server_default=text("NOW()"))
)

users = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column("username", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("password", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("admin", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column("approved", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column(
        "createdAt", sqlalchemy.dialects.postgresql.TIMESTAMP, server_default=text("NOW()")),
)


sessions = sqlalchemy.Table(
    'sessions',
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.ForeignKey(users.c.username))
)
