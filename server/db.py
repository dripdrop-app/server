import databases
import sqlalchemy
import os

DATABASE_URL = os.getenv('DATABASE_URL')
database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

music_jobs = sqlalchemy.Table(
    'music_jobs',
    metadata,
    sqlalchemy.Column("jobID", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("filename", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("youtubeURL", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("artworkURL", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("artist", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("album", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("grouping", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("completed", sqlalchemy.Boolean)
)
