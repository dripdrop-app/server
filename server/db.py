from os import O_RSYNC
import databases
import sqlalchemy
import os

DATABASE_URL = os.getenv('DATABASE_URL')
database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

music_jobs = sqlalchemy.Table(
    'music_jobs',
    metadata,
    sqlalchemy.Column("job_id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("completed", sqlalchemy.Boolean)
)
